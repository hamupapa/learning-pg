#include <iostream>
#include <string>
#include <list>

int main(void) {
    std::list<std::string> line;
    std::string input;
    int line_cnt = 2;

    // 標準入力から行数毎に文字列を格納する
    for (int i=0; i<line_cnt; ++i) {
        std::getline(std::cin, input);
        line.push_back(input);
    }

    // 文字列を出力する
    std::cout << "List of strings:" << std::endl;
    std::list<std::string>::iterator it = line.begin();
    for (it; it != line.end(); ++it) {
        std::cout << it->c_str() << std::endl;
    }

    // 2行目をスペース区切りでリストに格納する
    std::list<std::string> line2;
    std::string line2_input = *(++line.begin());
    std::string::size_type pos = 0;
    while ((pos = line2_input.find(' ')) != std::string::npos) {
        line2.push_back(line2_input.substr(0, pos));
        line2_input.erase(0, pos + 1);
    }
    line2.push_back(line2_input);

    // 文字列を出力する
    std::cout << "List of strings(line2):" << std::endl;
    std::list<std::string>::iterator it2 = line2.begin();
    for (it2; it2 != line2.end(); ++it2) {
        std::cout << it2->c_str() << std::endl;
    }

    return 0;
}
