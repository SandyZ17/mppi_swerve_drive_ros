"""Build-independent checks for ROS 2 package/launch/parameter compatibility."""
import ast
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_all_packages_use_ament():
    manifests = list((ROOT / 'src').rglob('package.xml'))
    assert len(manifests) == 11
    for path in manifests:
        package = ET.parse(path).getroot()
        assert package.findtext('export/build_type') == 'ament_cmake', path
        assert 'catkin' not in (path.parent / 'CMakeLists.txt').read_text(), path


def test_python_launch_files_parse():
    for path in (ROOT / 'src').rglob('*.launch.py'):
        ast.parse(path.read_text(), filename=str(path))
        if importlib.util.find_spec('launch') is not None:
            spec = importlib.util.spec_from_file_location('launch_under_test', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            assert module.generate_launch_description() is not None


def test_controller_parameter_types_and_dimensions():
    for name, dim in [('mppi_3d_a', 3), ('mppi_3d_b', 3), ('mppi_4d', 4), ('mppi_h', None)]:
        path = next((ROOT / 'src/control').rglob(name + '.yaml'))
        params = yaml.safe_load(path.read_text())['/**']['ros__parameters']
        assert params['ref_path_topic'] == '/reference_path'
        assert params['collision_costmap_topic'] == '/global_costmap/costmap'
        for prefix, size in ([('controller.', dim)] if dim else
                             [('controller.mode1.', 3), ('controller.mode2.', 4)]):
            assert len(params[prefix + 'sigma']) == size
            assert all(isinstance(x, float) for x in params[prefix + 'sigma'])
            assert params[prefix + 'num_samples'] > 0
            assert params[prefix + 'reference_velocity'] > 0


def test_model_has_ros2_control_and_native_sensor_plugins():
    path = ROOT / 'src/simulation/gazebo/world_handler/xacro/fwids_vehicle.xacro'
    model = ET.parse(path).getroot()
    plugins = {p.get('filename') for p in model.findall('.//plugin')}
    assert {'libgazebo_ros2_control.so', 'libgazebo_ros_ray_sensor.so', 'libgazebo_ros_p3d.so'} <= plugins
    assert model.find('ros2_control/hardware/plugin').text == 'gazebo_ros2_control/GazeboSystem'
    assert not model.findall('.//transmission')
