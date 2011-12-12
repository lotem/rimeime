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
    opencc_set_conversion_mode(od, OPENCC_CONVERSION_LIST_CANDIDATES);
    const int MAX_LEN = 1000;
    uint32_t inbuf[MAX_LEN];
    uint32_t outbuf[MAX_LEN];
    char result[MAX_LEN * 6];
    std::string line;
    while (std::getline(std::cin, line)) {
        uint32_t *end = utf8::unchecked::utf8to32(line.c_str(), line.c_str() + line.length(), inbuf);
        *end = L'\0';
        uint32_t *inptr = inbuf;
        size_t inlen = end - inptr;
        uint32_t *outptr = outbuf;
        size_t outlen = MAX_LEN;
        size_t converted = opencc_convert(od, &inptr, &inlen, &outptr, &outlen);
        *outptr = L'\0';
        if (!converted) {
            std::cerr << "error converting " << line << std::endl;
            opencc_close(od);
            return 1;
        }
        char *result_end = utf8::unchecked::utf32to8(outbuf, outptr, result);
        *result_end = '\0';
        std::cout << result << std::endl;
    }
    opencc_close(od);
    return 0;
}

