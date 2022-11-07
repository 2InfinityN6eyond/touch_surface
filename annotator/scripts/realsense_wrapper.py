import pyrealsense2 as rs
import numpy as np
import cv2
from multiprocessing import Process, Queue, Pipe, Value

class Device:
    def __init__(self, pipeline, pipeline_profile, product_line):
        self.pipeline = pipeline
        self.pipeline_profile = pipeline_profile
        self.product_line = product_line

def enumerate_connected_devices(context):
    connect_device = []

    for d in context.devices:
        if d.get_info(rs.camera_info.name).lower() != 'platform camera':
            serial = d.get_info(rs.camera_info.serial_number)
            product_line = d.get_info(rs.camera_info.product_line)
            device_info = (serial, product_line)
            connect_device.append(device_info)
    return connect_device

def post_process_depth_frame(
    depth_frame,
    decimation_magnitude=1.0,
    spatial_magnitude=2.0,
    spatial_smooth_alpha=0.5,
    spatial_smooth_delta=20,
    temporal_smooth_alpha=0.4,
    temporal_smooth_delta=20
):
    # Post processing possible only on the depth_frame
    assert (depth_frame.is_depth_frame())

    # Available filters and control options for the filters
    decimation_filter = rs.decimation_filter()
    spatial_filter = rs.spatial_filter()
    temporal_filter = rs.temporal_filter()

    filter_magnitude = rs.option.filter_magnitude
    filter_smooth_alpha = rs.option.filter_smooth_alpha
    filter_smooth_delta = rs.option.filter_smooth_delta

    # Apply the control parameters for the filter
    decimation_filter.set_option(filter_magnitude, decimation_magnitude)
    spatial_filter.set_option(filter_magnitude, spatial_magnitude)
    spatial_filter.set_option(filter_smooth_alpha, spatial_smooth_alpha)
    spatial_filter.set_option(filter_smooth_delta, spatial_smooth_delta)
    temporal_filter.set_option(filter_smooth_alpha, temporal_smooth_alpha)
    temporal_filter.set_option(filter_smooth_delta, temporal_smooth_delta)

    # Apply the filters
    filtered_frame = decimation_filter.process(depth_frame)
    filtered_frame = spatial_filter.process(filtered_frame)
    filtered_frame = temporal_filter.process(filtered_frame)

    return filtered_frame

class DeviceManager:
    def __init__(
        self,
        context,
        D400_pipeline_configuration,
    ):
        assert isinstance(context, type(rs.context()))
        assert isinstance(D400_pipeline_configuration, type(rs.config()))
        self._context = context
        self._available_devices = enumerate_connected_devices(context)
        self._enabled_devices = {} #serial numbers of te enabled devices
        self.D400_config = D400_pipeline_configuration
        self._frame_counter = 0

    def enable_device(self, device_info, enable_ir_emitter):
        pipeline = rs.pipeline()

        device_serial, product_line = device_info

        # Enable D400 device
        self.D400_config.enable_device(device_serial)
        pipeline_profile = pipeline.start(self.D400_config)

        # Set the acquisition parameters
        sensor = pipeline_profile.get_device().first_depth_sensor()
        if sensor.supports(rs.option.emitter_enabled):
            sensor.set_option(rs.option.emitter_enabled, 1 if enable_ir_emitter else 0)
        self._enabled_devices[device_serial] = (Device(pipeline, pipeline_profile, product_line))

    def enable_all_devices(self, enable_ir_emitter=False):
        print(f"{len(self._available_devices)} devices have been found")

        for device_info in self._available_devices:
            self.enable_device(device_info, enable_ir_emitter)

    def enable_emitter(self, enable_ir_emitter=True):
        for (device_serial, device) in self._enabled_devices.items():
            # Get the active profile and enable the emitter for all the connected devices
            sensor = device.pipeline_profile.get_device().first_depth_sensor()
            if not sensor.supports(rs.option.emitter_enabled):
                continue
            sensor.set_option(rs.option.emitter_enabled, 1 if enable_ir_emitter else 0)
            if enable_ir_emitter:
                sensor.set_option(rs.option.laser_power, 330)

    def load_settings_json(self, path_to_settings_file):
        with open(path_to_settings_file, 'r') as file:
        	json_text = file.read().strip()

        for (device_serial, device) in self._enabled_devices.items():
            if device.product_line == "L500":
                continue
            # Get the active profile and load the json file which contains settings readable by the realsense
            device = device.pipeline_profile.get_device()
            advanced_mode = rs.rs400_advanced_mode(device)
            advanced_mode.load_json(json_text)

    def poll_frames(self):
        frames = {}
        while len(frames) < len(self._enabled_devices.items()) :
            for (serial, device) in self._enabled_devices.items():
                streams = device.pipeline_profile.get_streams()
                frameset = device.pipeline.poll_for_frames() #frameset will be a pyrealsense2.composite_frame object
                if frameset.size() == len(streams):
                    dev_info = (serial, device.product_line)
                    frames[dev_info] = {}
                    for stream in streams:
                        if (rs.stream.infrared == stream.stream_type()):
                            frame = frameset.get_infrared_frame(stream.stream_index())
                            key_ = (stream.stream_type(), stream.stream_index())
                        else:
                            frame = frameset.first_or_default(stream.stream_type())
                            key_ = stream.stream_type()
                        #key_ = str(stream.stream_type()).split(".")[-1]
                        frames[dev_info][key_] = frame
        return frames

    def get_depth_shape(self):
        width = -1
        height = -1
        for (serial, device) in self._enabled_devices.items():
            for stream in device.pipeline_profile.get_streams():
                if (rs.stream.depth == stream.stream_type()):
                    width = stream.as_video_stream_profile().width()
                    height = stream.as_video_stream_profile().height()
        return width, height

    def get_device_intrinsics(self, frames):
        device_intrinsics = {}
        for (dev_info, frameset) in frames.items():
            serial = dev_info[0]
            device_intrinsics[serial] = {}
            for key, value in frameset.items():
                device_intrinsics[serial][key] = value.get_profile().as_video_stream_profile().get_intrinsics()
        return device_intrinsics

    def get_depth_to_color_extrinsics(self, frames):
        device_extrinsics = {}
        for (dev_info, frameset) in frames.items():
            serial = dev_info[0]
            device_extrinsics[serial] = frameset[
                rs.stream.depth].get_profile().as_video_stream_profile().get_extrinsics_to(
                frameset[rs.stream.color].get_profile())
        return device_extrinsics

    def disable_streams(self):
        self.D400_config.disable_all_streams()


class RealsenseWrapper(Process) :
    def __init__(
        self,
        to_data_bridge:Queue
    ) :
        super().__init__()
        self.daemon = False
        self.running = Value('b', True)

        self.to_data_bridget = to_data_bridge

    def run(self) :
        c = rs.config()
        #c.enable_stream(rs.stream.depth,       640, 480, rs.format.z16,  30)
        c.enable_stream(rs.stream.color,       1920, 1080, rs.format.bgr8, 30)
        #c.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8,   30)
        
        device_manager = DeviceManager(rs.context(), c)
        device_manager.enable_all_devices()

        devices = enumerate_connected_devices(rs.context())

        while True :
            frames = device_manager.poll_frames()

            #device_extrinsics = device_manager.get_depth_to_color_extrinsics(frames)
            #intrinsic = device_manager.get_device_intrinsics(frames)

            frame_1 = frames[devices[0]]
            frame_2 = frames[devices[1]]
            color_image_1 = np.asanyarray(frame_1[rs.stream.color].get_data())
            color_image_2 = np.asanyarray(frame_2[rs.stream.color].get_data())
            images = np.hstack((color_image_1, color_image_2))

            self.to_data_bridget.put({
                "color_1" : color_image_1,
                "color_2" : color_image_2
            })
            """
            self.to_data_bridget.put({
                "images": images,
                "data"  : {
                    "frames" : frames,
                    'intrinsic' : intrinsic,
                    "extrinsic" : device_extrinsics
                }
            })
            """
        device_manager.disable_streams()


if __name__ == "__main__":
    try:
        c = rs.config()
        c.enable_stream(rs.stream.depth,       640, 480, rs.format.z16,  30)
        c.enable_stream(rs.stream.color,       640, 480, rs.format.bgr8, 30)
        c.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8,   30)
        
        device_manager = DeviceManager(rs.context(), c)
        device_manager.enable_all_devices()

        devices = enumerate_connected_devices(rs.context())

        while True :
            frames = device_manager.poll_frames()

            device_extrinsics = device_manager.get_depth_to_color_extrinsics(frames)
            intrinsic = device_manager.get_device_intrinsics(frames)

            frame_1 = frames[devices[0]]
            frame_2 = frames[devices[1]]
            color_image_1 = np.asanyarray(frame_1[rs.stream.color].get_data())
            color_image_2 = np.asanyarray(frame_2[rs.stream.color].get_data())

            image = np.hstack((color_image_1, color_image_2))

            cv2.imshow("img", image)
            key = cv2.waitKey(1)
            # Press esc or 'q' to close the image window
            if key & 0xFF == ord('q') or key == 27:
                cv2.destroyAllWindows()
                break


    finally:
        device_manager.disable_streams()
