#include "mib2hspymainwindow.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    mib2hspyMainWindow w;
    w.show();
    return a.exec();
}
