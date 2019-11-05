from conans import ConanFile, CMake, tools
import codecs, os


class LibgeotiffConan(ConanFile):
	name = "libgeotiff"
	version = "1.5.1"
	license = "libgeotiff Licensing"
	description = "This library is designed to permit the extraction and parsing of the GeoTIFF Key directories, as well as definition and installation of GeoTIFF keys in new files."
	settings = "os", "compiler", "build_type", "arch"
	generators = "cmake"
	exports_sources = "CMakeLists.patch"
	_source_subfolder = "source_subfolder"
	options = {
		"shared": [True, False],
		"fPIC": [True, False],
		"tiff": [True, False],
		"zlib": [True, False],
		"jpeg": [True, False],
		"towgs84": [True, False],
		"utilities": [True, False]
	}
	default_options = {
		"shared": False,
		"fPIC": True,
		"tiff": True,
		"zlib": False,
		"jpeg": False,
		"towgs84": True,
		"utilities": True
	}
	requires = "proj/6.2.1@insanefactory/stable"

	def configure(self):
		if self.settings.compiler == "Visual Studio":
			del self.options.fPIC

	def requirements(self):
		if self.options.zlib:
			self.requires("zlib/1.2.11")
		if self.options.tiff:
			self.requires("libtiff/4.0.9")

	def source(self):
		# Download source and rename source directory.
		tools.get("http://download.osgeo.org/geotiff/libgeotiff/libgeotiff-%s.tar.gz" % self.version)
		os.rename("libgeotiff-%s" % self.version, self._source_subfolder)
		
		# Patch CMake files.
		tools.patch(base_path=self._source_subfolder, patch_file="CMakeLists.patch")
		with codecs.open("%s/libxtiff/CMakeLists.txt" % self._source_subfolder, "a", encoding="utf-8") as f:
			f.write("TARGET_LINK_LIBRARIES(xtiff CONAN_PKG::TIFF)")

	def build(self):
		cmake = CMake(self)
		cmake.definitions["WITH_TIFF"] = self.options.tiff
		cmake.definitions["WITH_ZLIB"] = self.options.zlib
		cmake.definitions["WITH_JPEG"] = self.options.jpeg
		cmake.definitions["WITH_TOWGS84"] = self.options.towgs84
		cmake.definitions["WITH_UTILITIES"] = self.options.utilities
		cmake.configure(source_folder=self._source_subfolder)
		cmake.build()
		cmake.install()

	def package(self):
		pass

	def package_info(self):
		needDebugSuffix = self.settings.os == "Windows" and self.settings.build_type == "Debug"
		self.cpp_info.libs = ["geotiff_d" if needDebugSuffix else "geotiff"]
