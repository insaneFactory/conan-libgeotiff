from conans import ConanFile, CMake, tools
import codecs, os


class LibgeotiffConan(ConanFile):
	name = "libgeotiff"
	version = "1.4.2"
	license = "libgeotiff Licensing"
	url = "https://github.com/insaneFactory/libgeotiff.git"
	description = "This library is designed to permit the extraction and parsing of the GeoTIFF Key directories, as well as definition and installation of GeoTIFF keys in new files."
	settings = "os", "compiler", "build_type", "arch"
	generators = "cmake"
	exports_sources = "CMakeLists.patch"
	source_subfolder = "source_subfolder"
	options = {
		"shared": [True, False],
		"fPIC": [True, False],
		"tiff": [True, False],
		"proj4": [True, False],
		"zlib": [True, False],
		"jpeg": [True, False],
		"towgs84": [True, False],
		"utilities": [True, False]
	}
	default_options = {
		"shared": False,
		"fPIC": True,
		"tiff": True,
		"proj4": True,
		"zlib": False,
		"jpeg": False,
		"towgs84": True,
		"utilities": True
	}

	def configure(self):
		if self.settings.compiler == "Visual Studio":
			del self.options.fPIC

	def requirements(self):
		if self.options.zlib:
			self.requires("zlib/1.2.11@conan/stable")
		if self.options.tiff:
			self.requires("libtiff/4.0.9@bincrafters/stable")
		if self.options.proj4:
			self.requires("proj4/5.2.0@insanefactory/stable")

	def source(self):
		# Download source and rename source directory.
		tools.get("http://download.osgeo.org/geotiff/libgeotiff/libgeotiff-%s.tar.gz" % self.version)
		os.rename("libgeotiff-%s" % self.version, self.source_subfolder)
		
		# Patch CMake files.
		tools.patch(base_path=self.source_subfolder, patch_file="CMakeLists.patch")
		with codecs.open("%s/libxtiff/CMakeLists.txt" % self.source_subfolder, "a", encoding="utf-8") as f:
			f.write("TARGET_LINK_LIBRARIES(xtiff CONAN_PKG::libtiff)")

	def build(self):
		cmake = CMake(self)
		cmake.definitions["WITH_TIFF"] = self.options.tiff
		cmake.definitions["WITH_PROJ4"] = self.options.proj4
		cmake.definitions["WITH_ZLIB"] = self.options.zlib
		cmake.definitions["WITH_JPEG"] = self.options.jpeg
		cmake.definitions["WITH_TOWGS84"] = self.options.towgs84
		cmake.definitions["WITH_UTILITIES"] = self.options.utilities
		cmake.configure(source_folder=self.source_subfolder)
		cmake.build()

	def package(self):
		self.copy("geo_config.h", dst="include")
		self.copy("*.h", dst="include", src=self.source_subfolder)
		self.copy("*.inc", dst="include", src=self.source_subfolder)
		self.copy("*.lib", dst="lib", keep_path=False)
		self.copy("*.dll", dst="bin", keep_path=False)
		self.copy("*.dylib*", dst="lib", keep_path=False)
		if self.options.shared:
			self.copy("*.so", dst="lib", keep_path=False)
		else:
			self.copy("*.a", dst="lib", keep_path=False)

	def package_info(self):
		needDebugSuffix = self.settings.os == "Windows" and self.settings.build_type == "Debug"
		self.cpp_info.libs = ["geotiff_d" if needDebugSuffix else "geotiff"]
		if not self.options.shared:
			self.cpp_info.libs.append("xtiff")
