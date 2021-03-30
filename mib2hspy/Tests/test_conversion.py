from unittest import TestCase
from mib2hspy import MicroscopeParameters, CalibratedParameter, Parameter
from mib2hspy import Converter
from mib2hspy import ReadError, WriteError, DimensionError, MIBError, HDRError, BlockfileError, CalibrationError, \
    FileNotSetError, ReshapeError, FileNameError, MedipixHDRcontent
from numpy import nan, isnan
import numpy as np

import hyperspy.api as hs
import pyxem as pxm
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# class TestGeneralConverter(TestCase):
#     def setUp(self):
#         self.microscope = MicroscopeParameters()
#         self.converter = Converter(self.microscope)
#         self.frame_size = 256  # Size of MIB frames. Must be changed if QUAD configurations are used!.
#         self.test_frame_data_path_1 = Path(__file__).parent.absolute() / 'test_data/test_CL30cm.mib'
#         self.test_frame_data_path_2 = Path(__file__).parent.absolute() / 'test_data/test_CL30cm_2.mib'
#         self.test_frame_data_path_3 = Path(__file__).parent.absolute() / 'test_data/test_CL30cm_corrupted.mib'
#
#     def test_construction(self):
#         """
#         Tests if the Converter object is created as intended.
#         :return:
#         """
#         self.assertIsInstance(self.converter.microscope_parameters, type(self.microscope))
#         self.assertIsNone(self.converter.data_path)
#         self.assertIsNone(self.converter.data)
#         self.assertIsNone(self.converter.hdr)
#         self.assertEqual(self.converter.frames, 0)
#         self.assertEqual(self.converter.dimension, 0)
#         self.assertEqual(self.converter.nx, 0)
#         self.assertEqual(self.converter.ny, 0)
#         self.assertEqual(self.converter.ndx, 0)
#         self.assertEqual(self.converter.ndy, 0)
#         self.assertTrue(isnan(self.converter.get_max_value()))
#
#         with self.assertRaises(FileNotSetError):
#             img_extent = self.converter.image_extent
#         with self.assertRaises(FileNotSetError):
#             scan_extent = self.converter.scan_extent
#
#     def test_data_path_assignment(self):
#         """
#         Tests whether the data_path setting is done correctly.
#         :return:
#         """
#         with self.assertRaises(FileNameError):
#             self.converter.data_path = 'test'
#         with self.assertRaises(FileNameError):
#             self.converter.data_path = 'test.mib'
#         with self.assertRaises(FileNameError):
#             self.converter.data_path = Path(__file__).absolute()
#
#         if self.test_frame_data_path_1.with_suffix('.hdr').exists():
#             with self.assertRaises(FileNameError):
#                 self.converter.data_path = self.test_frame_data_path_1.with_suffix('.hdr)')
#         else:
#             self.fail('Path to invalid file format test file "{path}" does not exist.'.format(
#                 path=self.test_frame_data_path_1.with_suffix('.hdr')))
#
#         if self.test_frame_data_path_1.exists():
#             # Check that all relevant parameters are None before assignment
#             self.assertIsNone(self.converter.data)
#             self.assertIsNone(self.converter.data_path)
#             self.assertIsNone(self.converter.hdr)
#
#             self.converter.data_path = self.test_frame_data_path_1
#             # Check that data and hdr are still None, while data_path is a Path
#             self.assertIsNone(self.converter.data)
#             self.assertIsNone(self.converter.hdr)
#             self.assertIsInstance(self.converter.data_path, Path)
#
#             # Check that you can set data_path to None
#             self.converter.data_path = None
#             self.assertIsNone(self.converter.data_path)
#         else:
#             self.fail('Path to testdata set "{self.test_deta_frame_path}" is not valid!'.format(self=self))
#
#     def test_read_mib(self):
#         """
#         Tests if -mib files are read correctly, or raises appropriate errors if not.
#         :return:
#         """
#         self.assertIsNone(self.converter.data, 'Data is not None at start of test')
#         self.assertIsNone(self.converter.hdr, 'HDR is not None at start of test')
#         self.assertIsNone(self.converter.data_path, 'Data path is not None at start of test')
#
#         # Check that data and hdr gets set to None if a corrupted MIB file is read
#         self.converter._data = 0
#         self.converter._hdr = 0
#         self.assertRaises(ReadError, self.converter.read_mib, self.test_frame_data_path_3)
#         self.assertIsNone(self.converter.data, 'Data is not reset to None after invalid reading')
#         self.assertIsNone(self.converter.hdr, 'HDR is not reset to None after invalid reading')
#
#         # Check that valid filename is accepted and HDR file is read
#         self.converter.read_mib(self.test_frame_data_path_1)
#         self.assertIsInstance(self.converter.data, pxm.LazyElectronDiffraction2D,
#                               'Data is not read as a LazyElectronDiffraction2D')
#         self.assertIsInstance(self.converter.hdr, MedipixHDRcontent,
#                               'HDR is not stored as a MedipixHDRcontent object after reading')
#
#         # Check that valid filename is accepted, but that HDR error is raised if hdr file is not present.
#         self.converter._hdr = 0
#         self.converter._data = None
#         self.assertRaises(HDRError, self.converter.read_mib, self.test_frame_data_path_2)
#         self.assertIsNone(self.converter.hdr)
#         self.assertIsInstance(self.converter.data, pxm.LazyElectronDiffraction2D)
#         self.assertEqual(self.converter.data_path, self.test_frame_data_path_2)
#
#     def test_single_frame(self):
#         self.converter.data_path = self.test_frame_data_path_1
#         self.converter.read_mib()
#         self.assertEqual(self.converter.frames, 1)
#         self.assertEqual(self.converter.ndx, self.frame_size)
#         self.assertEqual(self.converter.ndy, self.frame_size)
#         self.assertEqual(self.converter.nx, 1)
#         self.assertEqual(self.converter.ny, 1)
#         self.assertEqual(self.converter.dimension, 2)
#         self.assertRaises(DimensionError, lambda: self.converter.scan_extent)
#         self.assertRaises(DimensionError, self.converter.plot_vbf)


class TestDefaultConversion(TestCase):
    """
    Test case for when no path to a dataset is set, and when running functions on a default created object.
    """

    def setUp(self):
        self.microscope = MicroscopeParameters()
        self.converter = Converter(self.microscope)

    def test_data(self):
        self.assertIsNone(self.converter.data)

    def test_hdr(self):
        self.assertIsNone(self.converter.hdr)

    def test_data_path(self):
        self.assertIsNone(self.converter.data_path)

    def test_dimension(self):
        self.assertEqual(self.converter.dimension, 0)

    def test_frames(self):
        self.assertEqual(self.converter.frames, 0)

    def test_ndx(self):
        self.assertEqual(self.converter.ndx, 0)

    def test_ndy(self):
        self.assertEqual(self.converter.ndy, 0)

    def test_nx(self):
        self.assertEqual(self.converter.nx, 0)

    def test_ny(self):
        self.assertEqual(self.converter.ny, 0)

    def test_image_extent(self):
        with self.assertRaises(FileNotSetError):
            image_extent = self.converter.image_extent

    def test_scan_extent(self):
        with self.assertRaises(FileNotSetError):
            scan_extent = self.converter.scan_extent

    def test_read_mib(self):
        self.assertRaises(FileNotSetError, self.converter.read_mib)

    def test_get_max_value(self):
        self.assertTrue(isnan(self.converter.get_max_value()))

    def test_reshape(self):
        self.assertRaises(FileNotSetError, self.converter.reshape)

    def test_rechunk(self):
        self.assertRaises(FileNotSetError, self.converter.rechunk, 32)

    def test_downsample(self):
        self.assertRaises(FileNotSetError, self.converter.downsample, 'float32')

    def test_set_metadata(self):
        self.assertRaises(FileNotSetError, self.converter.set_metadata)

    def test_apply_calibrations(self):
        self.assertRaises(FileNotSetError, self.converter.apply_calibrations)

    def test_prepare_blockfile(self):
        self.assertRaises(FileNotSetError, self.converter.prepare_blockfile)

    def test_prepare_figure(self):
        self.skipTest('Preparation of Figures are not suited for testing at the moment')

    def test_plot_image(self):
        self.assertRaises(FileNotSetError, self.converter.plot_image)

    def test_plot_vbf(self):
        self.assertRaises(DimensionError, self.converter.plot_vbf)

    def test_get_square_vbf(self):
        self.assertRaises(FileNotSetError, self.converter.get_square_vbf)

    def test_get_circular_vbf(self):
        self.assertRaises(FileNotSetError, self.converter.get_circular_VBF)

    def test_get_vbf(self):
        self.assertRaises(FileNotSetError, self.converter.get_VBF, 'box')
        self.assertRaises(FileNotSetError, self.converter.get_VBF, 'circle')
        self.assertRaises(TypeError, self.converter.get_VBF)

    def test_write(self):
        self.assertRaises(WriteError, self.converter.write, '.hspy')

    def test_save_plot(self):
        self.assertRaises(FileNotSetError, self.converter.save_plot)


class TestValidDiffractionFrameConversion(TestCase):
    def setUp(self):
        self.microscope = MicroscopeParameters()
        self.microscope.microscope = '2100F'
        self.microscope.camera = 'Merlin'
        self.microscope.acceleration_voltage = 200000
        self.microscope.cameralength = (30, nan)

        self.converter = Converter(self.microscope)
        self.valid_data_path = Path(__file__).parent.absolute() / 'test_data/test_CL30cm.mib'
        self.frame_size = 256
        self.chunksize = 32
        self.new_dtype = 'uint8'
        self.old_dtype = '>u4'
        self.calibrationtable_path = Path(__file__).parent.absolute() / '../../Calibrations.xlsx'

        self.hdf_extensions = ['.hspy', '.hdf5']
        self.image_extensions = ['.tif', '.tiff', '.jpg', '.png']
        self.dpi = 300
        self.figsize_inches = 3

    def test_data_path(self):
        self.converter.data_path = self.valid_data_path
        self.assertIsNot(self.converter.data_path, self.valid_data_path)
        self.assertEqual(self.converter.data_path, self.valid_data_path)

    def test_frames(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.frames, 1)
        # Test further based on hyperspy functionality. Verify that there are only one frame in the stack. self.assertEqual(self.converter.data)

    def test_nx(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.nx, 1)

    def test_ny(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.ny, 1)

    def test_dimension(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.dimension, 2)
        # Test further based on the size of the signal!

    def test_ndx(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.ndx, self.frame_size)
        self.assertEqual(self.converter.ndx, self.converter.data.axes_manager[0].size)

    def test_ndy(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.ndy, self.frame_size)
        self.assertEqual(self.converter.ndy, self.converter.data.axes_manager[1].size)

    def test_image_extent(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertIsInstance(self.converter.image_extent,
                              (list, tuple))  # The image extent should be a list or a tuple
        self.assertEqual(len(self.converter.image_extent), 4)  # The length of the extent should be 4 elements
        self.assertTrue(all([isinstance(extent, (int, float)) for extent in
                             self.converter.image_extent]))  # The extent should only contain floats or integers!

    def test_scan_extent(self):
        self.converter.read_mib(self.valid_data_path)
        with self.assertRaises(DimensionError):
            scan_extent = self.converter.scan_extent

    def test_read_mib(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.valid_data_path, self.converter.data_path)
        self.assertIsNot(self.valid_data_path, self.converter.data_path)
        self.assertIsInstance(self.converter.data, pxm.LazyElectronDiffraction2D)
        self.assertIsInstance(self.converter.hdr, MedipixHDRcontent)

        # Check that the shape of the data is correct
        self.assertEqual(len(self.converter.data.data.shape), 2)
        self.assertEqual(self.converter.data.data.shape[0], self.frame_size)
        self.assertEqual(self.converter.data.data.shape[1], self.frame_size)

    def test_get_max_value(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertEqual(self.converter.get_max_value(), self.converter.data.max(axis=[0, 1]).data)

    def test_reshape(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.reshape)

    def test_rechunk(self):
        self.converter.read_mib(self.valid_data_path)
        self.converter.rechunk(self.chunksize)
        self.assertListEqual(list(self.converter.data.data.chunksize), [self.chunksize] * 2)

    def test_downsample(self):
        self.converter.read_mib(self.valid_data_path)
        old_dtype = self.converter.data.data.dtype
        old_max = self.converter.get_max_value()
        self.converter.downsample(self.new_dtype)
        new_dtype = self.converter.data.data.dtype
        new_max = self.converter.get_max_value()

        self.assertEqual(old_dtype, self.old_dtype)
        self.assertEqual(new_dtype, self.new_dtype)
        self.assertLessEqual(new_max, old_max, 'Maximum value after downsampling is not <= to old maximum!')
        if self.new_dtype == 'bool':
            val = 2 ** 1 - 1
            self.assertLessEqual(new_max, val,
                                 'Maximum value after downsampling to {self.new_dtype} is not <= {val}'.format(
                                     self=self, val=1))
        elif self.new_dtype == 'uint8':
            val = 2 ** 8 - 1
            self.assertLessEqual(new_max, val,
                                 'Maximum value after downsampling to {self.new_dtype} is not <= {val}'.format(
                                     self=self, val=1))
        elif self.new_dtype == 'uint16':
            val = 2 ** 16 - 1
            self.assertLessEqual(new_max, val,
                                 'Maximum value after downsampling to {self.new_dtype} is not <= {val}'.format(
                                     self=self, val=1))
        elif self.new_dtype == 'uint32':
            val = 2 ** 32 - 1
            self.assertLessEqual(new_max, val,
                                 'Maximum value after downsampling to {self.new_dtype} is not <= {val}'.format(
                                     self=self, val=1))
        else:
            pass

    def test_set_metadata(self):
        self.converter.read_mib(self.valid_data_path)
        old_metadata = self.converter.data.original_metadata.deepcopy()
        self.converter.set_metadata()
        new_metadata = self.converter.data.original_metadata
        self.assertDictEqual(new_metadata.as_dictionary()['Acquisition_instrument']['Parameters'],
                             self.microscope.get_parameters_as_dict())
        self.assertEqual(len(old_metadata), 0)
        self.assertTrue('Header' in new_metadata)

    def test_apply_calibrations(self):
        self.converter.read_mib(self.valid_data_path)
        calibration_table = pd.read_excel(self.calibrationtable_path, engine='openpyxl')
        self.microscope.set_values_from_calibrationtable(calibration_table)
        self.converter.apply_calibrations()
        self.assertEqual(self.converter.data.axes_manager[0].scale, self.microscope.diffraction_scale)
        self.assertEqual(self.converter.data.axes_manager[1].scale, self.microscope.diffraction_scale)
        self.assertEqual(self.converter.data.metadata.Acquisition_instrument.TEM.Detector.Diffraction.camera_length,
                         self.microscope.cameralength.value)
        self.assertEqual(self.converter.data.metadata.Acquisition_instrument.TEM.Detector.beam_energry,
                         self.microscope.acceleration_voltage.value)

    def test_prepare_blockfile(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.prepare_blockfile)

    def test_prepare_figure(self):
        self.skipTest('Preparation of Figures are not suited for testing at the moment')

    def test_plot_image(self):
        self.converter.read_mib(self.valid_data_path)
        fig = self.converter.plot_image()
        self.assertIsInstance(fig, plt.Figure)

    def test_plot_vbf(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.plot_vbf, 'box')
        self.assertRaises(DimensionError, self.converter.plot_vbf, 'circle')

    def test_get_square_vbf(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.get_square_vbf)
        self.assertRaises(DimensionError, self.converter.get_square_vbf, 0.0)
        self.assertRaises(DimensionError, self.converter.get_square_vbf, 0.0, 0.0)
        self.assertRaises(DimensionError, self.converter.get_square_vbf, None, 0.0)
        self.assertRaises(DimensionError, self.converter.get_square_vbf, 0.0, 0.0, 1)
        self.assertRaises(DimensionError, self.converter.get_square_vbf, None, None, 1)

    def test_get_circular_vbf(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF, 0.0)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF, 0.0, 0.0)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF, None, 0.0)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF, 0.0, 0.0, 1)
        self.assertRaises(DimensionError, self.converter.get_circular_VBF, None, None, 1)

    def test_get_vbf(self):
        self.converter.read_mib(self.valid_data_path)
        self.assertRaises(DimensionError, self.converter.get_VBF, 'box')
        self.assertRaises(DimensionError, self.converter.get_VBF, 'circle')
        self.assertRaises(ValueError, self.converter.get_VBF, 'test')
        self.assertRaises(TypeError, self.converter.get_VBF)

    def test_write(self):
        self.converter.read_mib(self.valid_data_path)
        calibration_table = pd.read_excel(self.calibrationtable_path, engine='openpyxl')
        self.microscope.set_values_from_calibrationtable(calibration_table)
        self.converter.apply_calibrations()
        self.converter.downsample('uint8')
        self.converter.rechunk(self.chunksize)

        # Test writing .hspy and .hdf5 files
        [self.converter.write(extension, overwrite=True) for extension in self.hdf_extensions]

        # Check that the files were written successfully and contain correct data and metadata
        for extension in self.hdf_extensions:
            s = hs.load(str(self.valid_data_path.with_suffix(extension)), lazy=True)
            print(extension)
            print(s)
            print(s.data.dtype)
            print(s.data)
            # Type
            self.assertIsInstance(s, pxm.LazyElectronDiffraction2D)
            # Dimension
            self.assertTrue(len(s.data.shape) == self.converter.dimension)

            # Data values
            self.assertTrue(all(self.converter.data - s.data == 0))

            # Data type
            self.assertTrue(s.data.dtype, self.new_dtype)
            self.assertTrue(s.data.dtype, self.converter.data.data.dtype)

            # Chunksize
            # self.assertListEqual(list(s.data.chunks), list(self.converter.data.data.chunks))
            # self.assertListEqual(list(s.data.chunksize), list(self.converter.data.data.chunksize))
            # self.assertListEqual(list(s.data.chunksize), [self.chunksize]*2)

            # Axes_manager values. Since nan==nan -> False, we do not need to check if there are any nans here
            for axis in range(self.converter.dimension):
                self.assertEqual(self.converter.data.axes_manager[axis].scale, s.axes_manager[axis].scale)
                self.assertEqual(self.converter.data.axes_manager[axis].name, s.axes_manager[axis].name)
                self.assertEqual(self.converter.data.axes_manager[axis].offset, s.axes_manager[axis].offset)
                self.assertEqual(self.converter.data.axes_manager[axis].units, s.axes_manager[axis].units)
                self.assertEqual(self.converter.data.axes_manager[axis].index, s.axes_manager[axis].index)

                self.assertEqual(s.axes_manager[axis].scale,
                                 self.microscope.diffraction_scale.value)  # Check this especially!

            # Check metadata [WIP]
            self.maxDiff = None
            # self.assertDictEqual(s.metadata.as_dictionary(), self.converter.data.metadata.as_dictionary())
            # self.assertDictEqual(s.original_metadata.as_dictionary(), self.converter.data.original_metadata.as_dictionary())

        # Test writing image files
        [self.converter.write(extension, overwrite=True) for extension in self.image_extensions]
        for extension in self.image_extensions:
            s = plt.imread(self.valid_data_path.with_suffix(extension))
            self.assertEqual(s.shape[0], self.figsize_inches * self.dpi)
            self.assertEqual(s.shape[1], self.figsize_inches * self.dpi)

    def test_save_plot(self):
        self.fail()
