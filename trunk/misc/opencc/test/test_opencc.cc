#include <iostream>
#include <string>
#include <stdlib.h>
#include <utf8.h>
#include "opencc.h"

int main() {
    const std::string config_file("zht2zhs.ini");
    opencc_t od = opencc_open(config_file.c_str());
    if (od == (opencc_t) -1) {
        std::cerr << "error opening opencc." << std::endl;
        return 1;
    }
    std::string line;
    while (std::getline(std::cin, line)) {
        uint32_t *inbuf = new uint32_t[line.length() + 1];
        uint32_t *end = utf8::unchecked::utf8to32(line.c_str(), line.c_str() + line.length(), inbuf);
        *end = L'\0';
        uint32_t *inptr = inbuf;
        size_t inlen = end - inptr;
        uint32_t *outbuf = new uint32_t[inlen + 1];
        uint32_t *outptr = outbuf;
        size_t outlen = inlen;
        size_t converted = opencc_convert(od, &inptr, &inlen, &outptr, &outlen);
        *outptr = L'\0';
        if (!converted) {
            std::cerr << "error converting " << line << std::endl;
            delete[] inbuf;
            delete[] outbuf;
            opencc_close(od);
            return 1;
        }
        char *result = new char[(outptr - outbuf) * 6 + 1];
        char *result_end = utf8::unchecked::utf32to8(outbuf, outptr, result);
        *result_end = '\0';
        std::cout << result << std::endl;
        delete result;
    }
    opencc_close(od);
    return 0;
}

