#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools


class LibwebpConan(ConanFile):
    name = "libwebp"
    version = "1.0.2"
    description = "library to encode and decode images in WebP format"
    url = "http://github.com/bincrafters/conan-libwebp"
    homepage = "https://github.com/webmproject/libwebp"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ("image","libwebp","webp","decoding","encoding")
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ['CMakeLists.txt',
                       '0001-fix-dll-export.patch',
                       '0002-enable-webpmux.patch']
    generators = 'cmake'
    _source_subfolder = "source_subfolder"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False],
               "with_simd": [True, False], "near_lossless": [True, False],
               "swap_16bit_csp": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'with_simd': True, 'near_lossless': True, 'swap_16bit_csp': False}

    def source(self):
        source_url = "https://github.com/webmproject/libwebp"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version),sha256="347cf85ddc3497832b5fa9eee62164a37b249c83adae0ba583093e039bf4881f")
        extracted_dir = self.name + "-" + self.version

        os.rename(extracted_dir, self._source_subfolder)

        tools.patch(base_path=self._source_subfolder,
            patch_file='0001-fix-dll-export.patch')

        tools.patch(base_path=self._source_subfolder,
            patch_file='0002-enable-webpmux.patch')

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _version_components(self):
        return [int(x) for x in self.version.split('.')]

    def _configure_cmake(self):
        cmake = CMake(self)
        # should be an option but it doesn't work yet
        cmake.definitions["WEBP_ENABLE_SIMD"] = self.options.with_simd
        if self._version_components[0] >= 1:
            cmake.definitions["WEBP_NEAR_LOSSLESS"] = self.options.near_lossless
        else:
            cmake.definitions["WEBP_ENABLE_NEAR_LOSSLESS"] = self.options.near_lossless
        cmake.definitions['WEBP_ENABLE_SWAP_16BIT_CSP'] = self.options.swap_16bit_csp
        # avoid finding system libs
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_GIF'] = True
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_PNG'] = True
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_TIFF'] = True
        cmake.definitions['CMAKE_DISABLE_FIND_PACKAGE_JPEG'] = True
        cmake.definitions['WEBP_BUILD_ANIM_UTILS'] = False
        cmake.definitions['WEBP_BUILD_CWEBP'] = False
        cmake.definitions['WEBP_BUILD_DWEBP'] = False
        cmake.definitions['WEBP_BUILD_IMG2WEBP'] = False
        cmake.definitions['WEBP_BUILD_GIF2WEBP'] = False
        cmake.definitions['WEBP_BUILD_VWEBP'] = False
        cmake.definitions['WEBP_BUILD_EXTRAS'] = False
        cmake.definitions['WEBP_BUILD_WEBPINFO'] = False
        cmake.definitions['WEBP_BUILD_WEBPMUX'] = False

        cmake.configure()

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("FindWEBP.cmake", dst=".", src=".")

    def package_info(self):
        self.cpp_info.libs = ['webpmux', 'webpdemux', 'webpdecoder', 'webp']
        if self.options.shared and self.settings.os == "Windows" and self.settings.compiler != 'Visual Studio':
            self.cpp_info.libs = [lib + '.dll' for lib in self.cpp_info.libs]
