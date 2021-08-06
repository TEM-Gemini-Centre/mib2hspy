/********************************************************************************
** Form generated from reading UI file 'stack_converter.ui'
**
** Created by: Qt User Interface Compiler version 5.12.8
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_STACK_CONVERTER_H
#define UI_STACK_CONVERTER_H

#include <QtCore/QDate>
#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDateEdit>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPlainTextEdit>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QScrollArea>
#include <QtWidgets/QSpacerItem>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QTableView>
#include <QtWidgets/QTextEdit>
#include <QtWidgets/QTreeWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QAction *actionVBF;
    QAction *actionFrames;
    QAction *actionExit;
    QAction *actionOpen;
    QAction *actionClose;
    QWidget *centralwidget;
    QVBoxLayout *verticalLayout_26;
    QHBoxLayout *horizontalLayout_4;
    QLabel *label;
    QLineEdit *dataPathLineEdit;
    QPushButton *browseDataButton;
    QPushButton *loadButton;
    QHBoxLayout *horizontalLayout_14;
    QVBoxLayout *verticalLayout_23;
    QHBoxLayout *horizontalLayout_13;
    QHBoxLayout *horizontalLayout_2;
    QPushButton *resetButton;
    QLabel *label_2;
    QLabel *signalLabel;
    QHBoxLayout *horizontalLayout_3;
    QVBoxLayout *verticalLayout_13;
    QGroupBox *groupBox;
    QVBoxLayout *verticalLayout_2;
    QGridLayout *gridLayout_10;
    QLabel *label_4;
    QLabel *framesLabel;
    QLabel *label_6;
    QLabel *label_7;
    QSpinBox *nXSpinBox;
    QSpinBox *nYSpinBox;
    QPushButton *reshapeButton;
    QGroupBox *groupBox_2;
    QVBoxLayout *verticalLayout;
    QGridLayout *gridLayout_8;
    QLabel *label_8;
    QLabel *chunksLabel;
    QLabel *label_10;
    QGridLayout *gridLayout_3;
    QLabel *label_36;
    QLabel *label_14;
    QLabel *label_35;
    QLabel *label_12;
    QSpinBox *chunkXSpinBox;
    QSpinBox *chunkYSpinBox;
    QSpinBox *chunkKxSpinBox;
    QSpinBox *chunkKySpinBox;
    QPushButton *rechunkButton;
    QGroupBox *groupBox_3;
    QVBoxLayout *verticalLayout_3;
    QPushButton *readDataInfoButton;
    QGridLayout *gridLayout_11;
    QLabel *label_11;
    QLabel *dtypeLabel;
    QLabel *maxValueLabel;
    QLabel *label_13;
    QLabel *label_15;
    QComboBox *dtypeComboBox;
    QPushButton *changeDtypeButton;
    QVBoxLayout *verticalLayout_22;
    QTabWidget *tabWidget_2;
    QWidget *tab_6;
    QGridLayout *gridLayout_7;
    QLabel *label_34;
    QLabel *label_33;
    QLineEdit *specimenLineEdit;
    QLineEdit *operatorLineEdit;
    QWidget *tab_4;
    QGridLayout *gridLayout_6;
    QLabel *label_30;
    QSpacerItem *horizontalSpacer;
    QDoubleSpinBox *xStage;
    QLabel *label_18;
    QSpacerItem *verticalSpacer_2;
    QDoubleSpinBox *alphaTilt;
    QDoubleSpinBox *betaTilt;
    QLabel *label_17;
    QLabel *label_32;
    QDoubleSpinBox *yStage;
    QDoubleSpinBox *zStage;
    QLabel *label_31;
    QCheckBox *rotationHolderCheckBox;
    QWidget *tab_5;
    QVBoxLayout *verticalLayout_12;
    QTextEdit *notesTextEdit;
    QTabWidget *tabWidget;
    QWidget *tab;
    QVBoxLayout *verticalLayout_11;
    QPlainTextEdit *axesManagerPlainTextEdit;
    QWidget *tab_2;
    QVBoxLayout *verticalLayout_9;
    QTreeWidget *metadataTreeWidget;
    QWidget *tab_3;
    QVBoxLayout *verticalLayout_10;
    QTreeWidget *originalMetadataTreeWidget;
    QHBoxLayout *horizontalLayout_12;
    QGroupBox *groupBox_4;
    QHBoxLayout *horizontalLayout_7;
    QPushButton *writeButton;
    QCheckBox *overwriteCheckBox;
    QGroupBox *VBFGroupBox;
    QGridLayout *gridLayout_2;
    QSpinBox *cYSpinBox;
    QLabel *label_3;
    QLabel *label_9;
    QSpinBox *cXSpinBox;
    QLabel *label_5;
    QSpinBox *widthSpinBox;
    QGroupBox *fileFormatGroupBox;
    QHBoxLayout *horizontalLayout;
    QCheckBox *hspyCheckBox;
    QCheckBox *hdfCheckBox;
    QCheckBox *jpgCheckBox;
    QCheckBox *pngCheckBox;
    QCheckBox *tifCheckBox;
    QSpacerItem *verticalSpacer;
    QVBoxLayout *verticalLayout_25;
    QVBoxLayout *verticalLayout_8;
    QHBoxLayout *horizontalLayout_6;
    QGroupBox *groupBox_9;
    QVBoxLayout *verticalLayout_7;
    QScrollArea *scrollArea;
    QWidget *scrollAreaWidgetContents;
    QGridLayout *gridLayout_4;
    QSpinBox *condenserApertureSpinBox;
    QCheckBox *acquisitionDateCheckBox;
    QDoubleSpinBox *highTensionSpinBox;
    QCheckBox *cameraCheckBox;
    QComboBox *microscopeComboBox;
    QComboBox *modeSelector;
    QLabel *label_25;
    QCheckBox *spotCheckBox;
    QCheckBox *cameraLengthCheckBox;
    QCheckBox *modeCheckBox;
    QDateEdit *acquisitionDate;
    QSpinBox *magnificationSpinBox;
    QComboBox *cameraComboBox;
    QLabel *label_21;
    QDoubleSpinBox *convergenceAngleSpinBox;
    QCheckBox *precessionFrequencyCheckBox;
    QCheckBox *alphaCheckBox;
    QCheckBox *microscopeCheckBox;
    QSpinBox *spotSpinBox;
    QDoubleSpinBox *spotSizeSpinBox;
    QSpinBox *alphaSpinBox;
    QLabel *label_23;
    QLabel *label_20;
    QCheckBox *highTensionCheckBox;
    QDoubleSpinBox *cameraLengthSpinBox;
    QLabel *label_19;
    QLabel *label_24;
    QCheckBox *convergenceAngleCheckBox;
    QCheckBox *magnificationCheckBox;
    QComboBox *magnificationSelector;
    QDoubleSpinBox *precessionFrequencySpinBox;
    QDoubleSpinBox *precessionAngleSpinBox;
    QCheckBox *spotSizeCheckBox;
    QCheckBox *condenserApertureCheckBox;
    QCheckBox *precessionAngleCheckBox;
    QLabel *label_22;
    QGroupBox *stepGroupBox;
    QGridLayout *gridLayout_5;
    QDoubleSpinBox *stepYSpinBox;
    QDoubleSpinBox *stepXSpinBox;
    QLabel *label_29;
    QLabel *label_28;
    QLabel *label_26;
    QLabel *label_27;
    QGroupBox *groupBox_8;
    QVBoxLayout *verticalLayout_6;
    QTableView *tableView;
    QPushButton *applyCalibrationButton;
    QGroupBox *groupBox_7;
    QVBoxLayout *verticalLayout_5;
    QHBoxLayout *horizontalLayout_5;
    QLabel *label_16;
    QLineEdit *calibrationPathLineEdit;
    QPushButton *browseCalibrationFileButton;
    QPushButton *showCalibrationsButton;
    QHBoxLayout *horizontalLayout_8;
    QPushButton *printConverterButton;
    QPushButton *refreshButton;
    QSpacerItem *horizontalSpacer_2;
    QMenuBar *menubar;
    QMenu *menuFile;
    QMenu *menuPlot;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QString::fromUtf8("MainWindow"));
        MainWindow->resize(1735, 864);
        actionVBF = new QAction(MainWindow);
        actionVBF->setObjectName(QString::fromUtf8("actionVBF"));
        actionFrames = new QAction(MainWindow);
        actionFrames->setObjectName(QString::fromUtf8("actionFrames"));
        actionExit = new QAction(MainWindow);
        actionExit->setObjectName(QString::fromUtf8("actionExit"));
        actionOpen = new QAction(MainWindow);
        actionOpen->setObjectName(QString::fromUtf8("actionOpen"));
        actionClose = new QAction(MainWindow);
        actionClose->setObjectName(QString::fromUtf8("actionClose"));
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        verticalLayout_26 = new QVBoxLayout(centralwidget);
        verticalLayout_26->setObjectName(QString::fromUtf8("verticalLayout_26"));
        horizontalLayout_4 = new QHBoxLayout();
        horizontalLayout_4->setObjectName(QString::fromUtf8("horizontalLayout_4"));
        label = new QLabel(centralwidget);
        label->setObjectName(QString::fromUtf8("label"));

        horizontalLayout_4->addWidget(label);

        dataPathLineEdit = new QLineEdit(centralwidget);
        dataPathLineEdit->setObjectName(QString::fromUtf8("dataPathLineEdit"));

        horizontalLayout_4->addWidget(dataPathLineEdit);

        browseDataButton = new QPushButton(centralwidget);
        browseDataButton->setObjectName(QString::fromUtf8("browseDataButton"));
        QSizePolicy sizePolicy(QSizePolicy::Maximum, QSizePolicy::Fixed);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(browseDataButton->sizePolicy().hasHeightForWidth());
        browseDataButton->setSizePolicy(sizePolicy);

        horizontalLayout_4->addWidget(browseDataButton);

        loadButton = new QPushButton(centralwidget);
        loadButton->setObjectName(QString::fromUtf8("loadButton"));
        sizePolicy.setHeightForWidth(loadButton->sizePolicy().hasHeightForWidth());
        loadButton->setSizePolicy(sizePolicy);

        horizontalLayout_4->addWidget(loadButton);


        verticalLayout_26->addLayout(horizontalLayout_4);

        horizontalLayout_14 = new QHBoxLayout();
        horizontalLayout_14->setObjectName(QString::fromUtf8("horizontalLayout_14"));
        verticalLayout_23 = new QVBoxLayout();
        verticalLayout_23->setObjectName(QString::fromUtf8("verticalLayout_23"));
        horizontalLayout_13 = new QHBoxLayout();
        horizontalLayout_13->setObjectName(QString::fromUtf8("horizontalLayout_13"));
        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setObjectName(QString::fromUtf8("horizontalLayout_2"));
        horizontalLayout_2->setSizeConstraint(QLayout::SetDefaultConstraint);
        resetButton = new QPushButton(centralwidget);
        resetButton->setObjectName(QString::fromUtf8("resetButton"));
        QSizePolicy sizePolicy1(QSizePolicy::Maximum, QSizePolicy::Maximum);
        sizePolicy1.setHorizontalStretch(0);
        sizePolicy1.setVerticalStretch(0);
        sizePolicy1.setHeightForWidth(resetButton->sizePolicy().hasHeightForWidth());
        resetButton->setSizePolicy(sizePolicy1);

        horizontalLayout_2->addWidget(resetButton);

        label_2 = new QLabel(centralwidget);
        label_2->setObjectName(QString::fromUtf8("label_2"));
        sizePolicy1.setHeightForWidth(label_2->sizePolicy().hasHeightForWidth());
        label_2->setSizePolicy(sizePolicy1);

        horizontalLayout_2->addWidget(label_2);

        signalLabel = new QLabel(centralwidget);
        signalLabel->setObjectName(QString::fromUtf8("signalLabel"));
        QSizePolicy sizePolicy2(QSizePolicy::Preferred, QSizePolicy::Maximum);
        sizePolicy2.setHorizontalStretch(0);
        sizePolicy2.setVerticalStretch(0);
        sizePolicy2.setHeightForWidth(signalLabel->sizePolicy().hasHeightForWidth());
        signalLabel->setSizePolicy(sizePolicy2);

        horizontalLayout_2->addWidget(signalLabel);


        horizontalLayout_13->addLayout(horizontalLayout_2);


        verticalLayout_23->addLayout(horizontalLayout_13);

        horizontalLayout_3 = new QHBoxLayout();
        horizontalLayout_3->setObjectName(QString::fromUtf8("horizontalLayout_3"));
        horizontalLayout_3->setSizeConstraint(QLayout::SetDefaultConstraint);
        verticalLayout_13 = new QVBoxLayout();
        verticalLayout_13->setObjectName(QString::fromUtf8("verticalLayout_13"));
        groupBox = new QGroupBox(centralwidget);
        groupBox->setObjectName(QString::fromUtf8("groupBox"));
        verticalLayout_2 = new QVBoxLayout(groupBox);
        verticalLayout_2->setObjectName(QString::fromUtf8("verticalLayout_2"));
        gridLayout_10 = new QGridLayout();
        gridLayout_10->setObjectName(QString::fromUtf8("gridLayout_10"));
        label_4 = new QLabel(groupBox);
        label_4->setObjectName(QString::fromUtf8("label_4"));
        QSizePolicy sizePolicy3(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy3.setHorizontalStretch(0);
        sizePolicy3.setVerticalStretch(0);
        sizePolicy3.setHeightForWidth(label_4->sizePolicy().hasHeightForWidth());
        label_4->setSizePolicy(sizePolicy3);

        gridLayout_10->addWidget(label_4, 0, 0, 1, 1);

        framesLabel = new QLabel(groupBox);
        framesLabel->setObjectName(QString::fromUtf8("framesLabel"));

        gridLayout_10->addWidget(framesLabel, 0, 1, 1, 1);

        label_6 = new QLabel(groupBox);
        label_6->setObjectName(QString::fromUtf8("label_6"));
        sizePolicy3.setHeightForWidth(label_6->sizePolicy().hasHeightForWidth());
        label_6->setSizePolicy(sizePolicy3);

        gridLayout_10->addWidget(label_6, 1, 0, 1, 1);

        label_7 = new QLabel(groupBox);
        label_7->setObjectName(QString::fromUtf8("label_7"));

        gridLayout_10->addWidget(label_7, 2, 0, 1, 1);

        nXSpinBox = new QSpinBox(groupBox);
        nXSpinBox->setObjectName(QString::fromUtf8("nXSpinBox"));
        sizePolicy.setHeightForWidth(nXSpinBox->sizePolicy().hasHeightForWidth());
        nXSpinBox->setSizePolicy(sizePolicy);
        nXSpinBox->setMinimum(0);
        nXSpinBox->setMaximum(4096);

        gridLayout_10->addWidget(nXSpinBox, 1, 1, 1, 1);

        nYSpinBox = new QSpinBox(groupBox);
        nYSpinBox->setObjectName(QString::fromUtf8("nYSpinBox"));
        sizePolicy.setHeightForWidth(nYSpinBox->sizePolicy().hasHeightForWidth());
        nYSpinBox->setSizePolicy(sizePolicy);
        nYSpinBox->setMinimum(0);
        nYSpinBox->setMaximum(4096);

        gridLayout_10->addWidget(nYSpinBox, 2, 1, 1, 1);


        verticalLayout_2->addLayout(gridLayout_10);

        reshapeButton = new QPushButton(groupBox);
        reshapeButton->setObjectName(QString::fromUtf8("reshapeButton"));
        QSizePolicy sizePolicy4(QSizePolicy::Preferred, QSizePolicy::Fixed);
        sizePolicy4.setHorizontalStretch(0);
        sizePolicy4.setVerticalStretch(0);
        sizePolicy4.setHeightForWidth(reshapeButton->sizePolicy().hasHeightForWidth());
        reshapeButton->setSizePolicy(sizePolicy4);

        verticalLayout_2->addWidget(reshapeButton);


        verticalLayout_13->addWidget(groupBox);

        groupBox_2 = new QGroupBox(centralwidget);
        groupBox_2->setObjectName(QString::fromUtf8("groupBox_2"));
        verticalLayout = new QVBoxLayout(groupBox_2);
        verticalLayout->setObjectName(QString::fromUtf8("verticalLayout"));
        gridLayout_8 = new QGridLayout();
        gridLayout_8->setObjectName(QString::fromUtf8("gridLayout_8"));
        label_8 = new QLabel(groupBox_2);
        label_8->setObjectName(QString::fromUtf8("label_8"));
        QSizePolicy sizePolicy5(QSizePolicy::Maximum, QSizePolicy::Preferred);
        sizePolicy5.setHorizontalStretch(0);
        sizePolicy5.setVerticalStretch(0);
        sizePolicy5.setHeightForWidth(label_8->sizePolicy().hasHeightForWidth());
        label_8->setSizePolicy(sizePolicy5);

        gridLayout_8->addWidget(label_8, 0, 0, 1, 1);

        chunksLabel = new QLabel(groupBox_2);
        chunksLabel->setObjectName(QString::fromUtf8("chunksLabel"));

        gridLayout_8->addWidget(chunksLabel, 0, 1, 1, 1);


        verticalLayout->addLayout(gridLayout_8);

        label_10 = new QLabel(groupBox_2);
        label_10->setObjectName(QString::fromUtf8("label_10"));
        sizePolicy5.setHeightForWidth(label_10->sizePolicy().hasHeightForWidth());
        label_10->setSizePolicy(sizePolicy5);

        verticalLayout->addWidget(label_10);

        gridLayout_3 = new QGridLayout();
        gridLayout_3->setObjectName(QString::fromUtf8("gridLayout_3"));
        label_36 = new QLabel(groupBox_2);
        label_36->setObjectName(QString::fromUtf8("label_36"));

        gridLayout_3->addWidget(label_36, 0, 3, 1, 1);

        label_14 = new QLabel(groupBox_2);
        label_14->setObjectName(QString::fromUtf8("label_14"));

        gridLayout_3->addWidget(label_14, 0, 1, 1, 1);

        label_35 = new QLabel(groupBox_2);
        label_35->setObjectName(QString::fromUtf8("label_35"));

        gridLayout_3->addWidget(label_35, 0, 2, 1, 1);

        label_12 = new QLabel(groupBox_2);
        label_12->setObjectName(QString::fromUtf8("label_12"));

        gridLayout_3->addWidget(label_12, 0, 0, 1, 1);

        chunkXSpinBox = new QSpinBox(groupBox_2);
        chunkXSpinBox->setObjectName(QString::fromUtf8("chunkXSpinBox"));
        sizePolicy.setHeightForWidth(chunkXSpinBox->sizePolicy().hasHeightForWidth());
        chunkXSpinBox->setSizePolicy(sizePolicy);
        chunkXSpinBox->setMinimum(1);
        chunkXSpinBox->setValue(32);

        gridLayout_3->addWidget(chunkXSpinBox, 1, 0, 1, 1);

        chunkYSpinBox = new QSpinBox(groupBox_2);
        chunkYSpinBox->setObjectName(QString::fromUtf8("chunkYSpinBox"));
        sizePolicy.setHeightForWidth(chunkYSpinBox->sizePolicy().hasHeightForWidth());
        chunkYSpinBox->setSizePolicy(sizePolicy);
        chunkYSpinBox->setMinimum(1);
        chunkYSpinBox->setValue(32);

        gridLayout_3->addWidget(chunkYSpinBox, 1, 1, 1, 1);

        chunkKxSpinBox = new QSpinBox(groupBox_2);
        chunkKxSpinBox->setObjectName(QString::fromUtf8("chunkKxSpinBox"));
        sizePolicy.setHeightForWidth(chunkKxSpinBox->sizePolicy().hasHeightForWidth());
        chunkKxSpinBox->setSizePolicy(sizePolicy);
        chunkKxSpinBox->setMinimum(1);
        chunkKxSpinBox->setValue(32);

        gridLayout_3->addWidget(chunkKxSpinBox, 1, 2, 1, 1);

        chunkKySpinBox = new QSpinBox(groupBox_2);
        chunkKySpinBox->setObjectName(QString::fromUtf8("chunkKySpinBox"));
        sizePolicy.setHeightForWidth(chunkKySpinBox->sizePolicy().hasHeightForWidth());
        chunkKySpinBox->setSizePolicy(sizePolicy);
        chunkKySpinBox->setMinimum(1);
        chunkKySpinBox->setValue(32);

        gridLayout_3->addWidget(chunkKySpinBox, 1, 3, 1, 1);


        verticalLayout->addLayout(gridLayout_3);

        rechunkButton = new QPushButton(groupBox_2);
        rechunkButton->setObjectName(QString::fromUtf8("rechunkButton"));
        sizePolicy4.setHeightForWidth(rechunkButton->sizePolicy().hasHeightForWidth());
        rechunkButton->setSizePolicy(sizePolicy4);

        verticalLayout->addWidget(rechunkButton);


        verticalLayout_13->addWidget(groupBox_2);

        groupBox_3 = new QGroupBox(centralwidget);
        groupBox_3->setObjectName(QString::fromUtf8("groupBox_3"));
        verticalLayout_3 = new QVBoxLayout(groupBox_3);
        verticalLayout_3->setObjectName(QString::fromUtf8("verticalLayout_3"));
        readDataInfoButton = new QPushButton(groupBox_3);
        readDataInfoButton->setObjectName(QString::fromUtf8("readDataInfoButton"));

        verticalLayout_3->addWidget(readDataInfoButton);

        gridLayout_11 = new QGridLayout();
        gridLayout_11->setObjectName(QString::fromUtf8("gridLayout_11"));
        label_11 = new QLabel(groupBox_3);
        label_11->setObjectName(QString::fromUtf8("label_11"));
        sizePolicy5.setHeightForWidth(label_11->sizePolicy().hasHeightForWidth());
        label_11->setSizePolicy(sizePolicy5);

        gridLayout_11->addWidget(label_11, 0, 0, 1, 1);

        dtypeLabel = new QLabel(groupBox_3);
        dtypeLabel->setObjectName(QString::fromUtf8("dtypeLabel"));

        gridLayout_11->addWidget(dtypeLabel, 0, 1, 1, 1);

        maxValueLabel = new QLabel(groupBox_3);
        maxValueLabel->setObjectName(QString::fromUtf8("maxValueLabel"));

        gridLayout_11->addWidget(maxValueLabel, 1, 1, 1, 1);

        label_13 = new QLabel(groupBox_3);
        label_13->setObjectName(QString::fromUtf8("label_13"));
        sizePolicy5.setHeightForWidth(label_13->sizePolicy().hasHeightForWidth());
        label_13->setSizePolicy(sizePolicy5);

        gridLayout_11->addWidget(label_13, 1, 0, 1, 1);

        label_15 = new QLabel(groupBox_3);
        label_15->setObjectName(QString::fromUtf8("label_15"));
        sizePolicy5.setHeightForWidth(label_15->sizePolicy().hasHeightForWidth());
        label_15->setSizePolicy(sizePolicy5);

        gridLayout_11->addWidget(label_15, 2, 0, 1, 1);

        dtypeComboBox = new QComboBox(groupBox_3);
        dtypeComboBox->addItem(QString());
        dtypeComboBox->addItem(QString());
        dtypeComboBox->addItem(QString());
        dtypeComboBox->addItem(QString());
        dtypeComboBox->setObjectName(QString::fromUtf8("dtypeComboBox"));

        gridLayout_11->addWidget(dtypeComboBox, 2, 1, 1, 1);


        verticalLayout_3->addLayout(gridLayout_11);

        changeDtypeButton = new QPushButton(groupBox_3);
        changeDtypeButton->setObjectName(QString::fromUtf8("changeDtypeButton"));

        verticalLayout_3->addWidget(changeDtypeButton);


        verticalLayout_13->addWidget(groupBox_3);


        horizontalLayout_3->addLayout(verticalLayout_13);

        verticalLayout_22 = new QVBoxLayout();
        verticalLayout_22->setObjectName(QString::fromUtf8("verticalLayout_22"));
        tabWidget_2 = new QTabWidget(centralwidget);
        tabWidget_2->setObjectName(QString::fromUtf8("tabWidget_2"));
        QSizePolicy sizePolicy6(QSizePolicy::Expanding, QSizePolicy::Maximum);
        sizePolicy6.setHorizontalStretch(0);
        sizePolicy6.setVerticalStretch(0);
        sizePolicy6.setHeightForWidth(tabWidget_2->sizePolicy().hasHeightForWidth());
        tabWidget_2->setSizePolicy(sizePolicy6);
        tab_6 = new QWidget();
        tab_6->setObjectName(QString::fromUtf8("tab_6"));
        gridLayout_7 = new QGridLayout(tab_6);
        gridLayout_7->setObjectName(QString::fromUtf8("gridLayout_7"));
        label_34 = new QLabel(tab_6);
        label_34->setObjectName(QString::fromUtf8("label_34"));

        gridLayout_7->addWidget(label_34, 1, 0, 1, 1);

        label_33 = new QLabel(tab_6);
        label_33->setObjectName(QString::fromUtf8("label_33"));

        gridLayout_7->addWidget(label_33, 0, 0, 1, 1);

        specimenLineEdit = new QLineEdit(tab_6);
        specimenLineEdit->setObjectName(QString::fromUtf8("specimenLineEdit"));

        gridLayout_7->addWidget(specimenLineEdit, 1, 1, 1, 1);

        operatorLineEdit = new QLineEdit(tab_6);
        operatorLineEdit->setObjectName(QString::fromUtf8("operatorLineEdit"));

        gridLayout_7->addWidget(operatorLineEdit, 0, 1, 1, 1);

        tabWidget_2->addTab(tab_6, QString());
        tab_4 = new QWidget();
        tab_4->setObjectName(QString::fromUtf8("tab_4"));
        gridLayout_6 = new QGridLayout(tab_4);
        gridLayout_6->setObjectName(QString::fromUtf8("gridLayout_6"));
        label_30 = new QLabel(tab_4);
        label_30->setObjectName(QString::fromUtf8("label_30"));

        gridLayout_6->addWidget(label_30, 0, 2, 1, 1);

        horizontalSpacer = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        gridLayout_6->addItem(horizontalSpacer, 0, 7, 1, 1);

        xStage = new QDoubleSpinBox(tab_4);
        xStage->setObjectName(QString::fromUtf8("xStage"));

        gridLayout_6->addWidget(xStage, 1, 0, 1, 1);

        label_18 = new QLabel(tab_4);
        label_18->setObjectName(QString::fromUtf8("label_18"));

        gridLayout_6->addWidget(label_18, 0, 1, 1, 1);

        verticalSpacer_2 = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        gridLayout_6->addItem(verticalSpacer_2, 2, 0, 1, 1);

        alphaTilt = new QDoubleSpinBox(tab_4);
        alphaTilt->setObjectName(QString::fromUtf8("alphaTilt"));

        gridLayout_6->addWidget(alphaTilt, 1, 4, 1, 1);

        betaTilt = new QDoubleSpinBox(tab_4);
        betaTilt->setObjectName(QString::fromUtf8("betaTilt"));

        gridLayout_6->addWidget(betaTilt, 1, 5, 1, 1);

        label_17 = new QLabel(tab_4);
        label_17->setObjectName(QString::fromUtf8("label_17"));

        gridLayout_6->addWidget(label_17, 0, 0, 1, 1);

        label_32 = new QLabel(tab_4);
        label_32->setObjectName(QString::fromUtf8("label_32"));

        gridLayout_6->addWidget(label_32, 0, 5, 1, 1);

        yStage = new QDoubleSpinBox(tab_4);
        yStage->setObjectName(QString::fromUtf8("yStage"));

        gridLayout_6->addWidget(yStage, 1, 1, 1, 1);

        zStage = new QDoubleSpinBox(tab_4);
        zStage->setObjectName(QString::fromUtf8("zStage"));

        gridLayout_6->addWidget(zStage, 1, 2, 1, 2);

        label_31 = new QLabel(tab_4);
        label_31->setObjectName(QString::fromUtf8("label_31"));

        gridLayout_6->addWidget(label_31, 0, 3, 1, 2);

        rotationHolderCheckBox = new QCheckBox(tab_4);
        rotationHolderCheckBox->setObjectName(QString::fromUtf8("rotationHolderCheckBox"));

        gridLayout_6->addWidget(rotationHolderCheckBox, 1, 6, 1, 1);

        tabWidget_2->addTab(tab_4, QString());
        tab_5 = new QWidget();
        tab_5->setObjectName(QString::fromUtf8("tab_5"));
        verticalLayout_12 = new QVBoxLayout(tab_5);
        verticalLayout_12->setObjectName(QString::fromUtf8("verticalLayout_12"));
        notesTextEdit = new QTextEdit(tab_5);
        notesTextEdit->setObjectName(QString::fromUtf8("notesTextEdit"));
        sizePolicy6.setHeightForWidth(notesTextEdit->sizePolicy().hasHeightForWidth());
        notesTextEdit->setSizePolicy(sizePolicy6);
        notesTextEdit->setMinimumSize(QSize(0, 0));
        notesTextEdit->setMaximumSize(QSize(16777215, 100));

        verticalLayout_12->addWidget(notesTextEdit);

        tabWidget_2->addTab(tab_5, QString());

        verticalLayout_22->addWidget(tabWidget_2);

        tabWidget = new QTabWidget(centralwidget);
        tabWidget->setObjectName(QString::fromUtf8("tabWidget"));
        QSizePolicy sizePolicy7(QSizePolicy::Expanding, QSizePolicy::Preferred);
        sizePolicy7.setHorizontalStretch(0);
        sizePolicy7.setVerticalStretch(0);
        sizePolicy7.setHeightForWidth(tabWidget->sizePolicy().hasHeightForWidth());
        tabWidget->setSizePolicy(sizePolicy7);
        tab = new QWidget();
        tab->setObjectName(QString::fromUtf8("tab"));
        verticalLayout_11 = new QVBoxLayout(tab);
        verticalLayout_11->setObjectName(QString::fromUtf8("verticalLayout_11"));
        axesManagerPlainTextEdit = new QPlainTextEdit(tab);
        axesManagerPlainTextEdit->setObjectName(QString::fromUtf8("axesManagerPlainTextEdit"));

        verticalLayout_11->addWidget(axesManagerPlainTextEdit);

        tabWidget->addTab(tab, QString());
        tab_2 = new QWidget();
        tab_2->setObjectName(QString::fromUtf8("tab_2"));
        verticalLayout_9 = new QVBoxLayout(tab_2);
        verticalLayout_9->setObjectName(QString::fromUtf8("verticalLayout_9"));
        metadataTreeWidget = new QTreeWidget(tab_2);
        QTreeWidgetItem *__qtreewidgetitem = new QTreeWidgetItem();
        __qtreewidgetitem->setText(0, QString::fromUtf8("1"));
        metadataTreeWidget->setHeaderItem(__qtreewidgetitem);
        metadataTreeWidget->setObjectName(QString::fromUtf8("metadataTreeWidget"));

        verticalLayout_9->addWidget(metadataTreeWidget);

        tabWidget->addTab(tab_2, QString());
        tab_3 = new QWidget();
        tab_3->setObjectName(QString::fromUtf8("tab_3"));
        verticalLayout_10 = new QVBoxLayout(tab_3);
        verticalLayout_10->setObjectName(QString::fromUtf8("verticalLayout_10"));
        originalMetadataTreeWidget = new QTreeWidget(tab_3);
        QTreeWidgetItem *__qtreewidgetitem1 = new QTreeWidgetItem();
        __qtreewidgetitem1->setText(0, QString::fromUtf8("1"));
        originalMetadataTreeWidget->setHeaderItem(__qtreewidgetitem1);
        originalMetadataTreeWidget->setObjectName(QString::fromUtf8("originalMetadataTreeWidget"));
        sizePolicy7.setHeightForWidth(originalMetadataTreeWidget->sizePolicy().hasHeightForWidth());
        originalMetadataTreeWidget->setSizePolicy(sizePolicy7);

        verticalLayout_10->addWidget(originalMetadataTreeWidget);

        tabWidget->addTab(tab_3, QString());

        verticalLayout_22->addWidget(tabWidget);


        horizontalLayout_3->addLayout(verticalLayout_22);


        verticalLayout_23->addLayout(horizontalLayout_3);

        horizontalLayout_12 = new QHBoxLayout();
        horizontalLayout_12->setObjectName(QString::fromUtf8("horizontalLayout_12"));
        groupBox_4 = new QGroupBox(centralwidget);
        groupBox_4->setObjectName(QString::fromUtf8("groupBox_4"));
        horizontalLayout_7 = new QHBoxLayout(groupBox_4);
        horizontalLayout_7->setObjectName(QString::fromUtf8("horizontalLayout_7"));
        writeButton = new QPushButton(groupBox_4);
        writeButton->setObjectName(QString::fromUtf8("writeButton"));

        horizontalLayout_7->addWidget(writeButton);

        overwriteCheckBox = new QCheckBox(groupBox_4);
        overwriteCheckBox->setObjectName(QString::fromUtf8("overwriteCheckBox"));
        sizePolicy.setHeightForWidth(overwriteCheckBox->sizePolicy().hasHeightForWidth());
        overwriteCheckBox->setSizePolicy(sizePolicy);
        overwriteCheckBox->setChecked(true);

        horizontalLayout_7->addWidget(overwriteCheckBox);

        VBFGroupBox = new QGroupBox(groupBox_4);
        VBFGroupBox->setObjectName(QString::fromUtf8("VBFGroupBox"));
        VBFGroupBox->setCheckable(true);
        gridLayout_2 = new QGridLayout(VBFGroupBox);
        gridLayout_2->setObjectName(QString::fromUtf8("gridLayout_2"));
        cYSpinBox = new QSpinBox(VBFGroupBox);
        cYSpinBox->setObjectName(QString::fromUtf8("cYSpinBox"));
        cYSpinBox->setMaximum(255);
        cYSpinBox->setValue(128);

        gridLayout_2->addWidget(cYSpinBox, 1, 3, 1, 1);

        label_3 = new QLabel(VBFGroupBox);
        label_3->setObjectName(QString::fromUtf8("label_3"));

        gridLayout_2->addWidget(label_3, 1, 0, 1, 1);

        label_9 = new QLabel(VBFGroupBox);
        label_9->setObjectName(QString::fromUtf8("label_9"));

        gridLayout_2->addWidget(label_9, 1, 4, 1, 1);

        cXSpinBox = new QSpinBox(VBFGroupBox);
        cXSpinBox->setObjectName(QString::fromUtf8("cXSpinBox"));
        cXSpinBox->setMaximum(255);
        cXSpinBox->setValue(128);

        gridLayout_2->addWidget(cXSpinBox, 1, 1, 1, 1);

        label_5 = new QLabel(VBFGroupBox);
        label_5->setObjectName(QString::fromUtf8("label_5"));

        gridLayout_2->addWidget(label_5, 1, 2, 1, 1);

        widthSpinBox = new QSpinBox(VBFGroupBox);
        widthSpinBox->setObjectName(QString::fromUtf8("widthSpinBox"));
        widthSpinBox->setMaximum(255);
        widthSpinBox->setValue(10);

        gridLayout_2->addWidget(widthSpinBox, 1, 5, 1, 1);


        horizontalLayout_7->addWidget(VBFGroupBox);

        fileFormatGroupBox = new QGroupBox(groupBox_4);
        fileFormatGroupBox->setObjectName(QString::fromUtf8("fileFormatGroupBox"));
        horizontalLayout = new QHBoxLayout(fileFormatGroupBox);
        horizontalLayout->setObjectName(QString::fromUtf8("horizontalLayout"));
        hspyCheckBox = new QCheckBox(fileFormatGroupBox);
        hspyCheckBox->setObjectName(QString::fromUtf8("hspyCheckBox"));
        hspyCheckBox->setChecked(true);

        horizontalLayout->addWidget(hspyCheckBox);

        hdfCheckBox = new QCheckBox(fileFormatGroupBox);
        hdfCheckBox->setObjectName(QString::fromUtf8("hdfCheckBox"));

        horizontalLayout->addWidget(hdfCheckBox);

        jpgCheckBox = new QCheckBox(fileFormatGroupBox);
        jpgCheckBox->setObjectName(QString::fromUtf8("jpgCheckBox"));

        horizontalLayout->addWidget(jpgCheckBox);

        pngCheckBox = new QCheckBox(fileFormatGroupBox);
        pngCheckBox->setObjectName(QString::fromUtf8("pngCheckBox"));

        horizontalLayout->addWidget(pngCheckBox);

        tifCheckBox = new QCheckBox(fileFormatGroupBox);
        tifCheckBox->setObjectName(QString::fromUtf8("tifCheckBox"));

        horizontalLayout->addWidget(tifCheckBox);


        horizontalLayout_7->addWidget(fileFormatGroupBox);


        horizontalLayout_12->addWidget(groupBox_4);


        verticalLayout_23->addLayout(horizontalLayout_12);

        verticalSpacer = new QSpacerItem(20, 40, QSizePolicy::Minimum, QSizePolicy::Expanding);

        verticalLayout_23->addItem(verticalSpacer);


        horizontalLayout_14->addLayout(verticalLayout_23);

        verticalLayout_25 = new QVBoxLayout();
        verticalLayout_25->setObjectName(QString::fromUtf8("verticalLayout_25"));
        verticalLayout_8 = new QVBoxLayout();
        verticalLayout_8->setObjectName(QString::fromUtf8("verticalLayout_8"));
        horizontalLayout_6 = new QHBoxLayout();
        horizontalLayout_6->setObjectName(QString::fromUtf8("horizontalLayout_6"));
        groupBox_9 = new QGroupBox(centralwidget);
        groupBox_9->setObjectName(QString::fromUtf8("groupBox_9"));
        sizePolicy5.setHeightForWidth(groupBox_9->sizePolicy().hasHeightForWidth());
        groupBox_9->setSizePolicy(sizePolicy5);
        verticalLayout_7 = new QVBoxLayout(groupBox_9);
        verticalLayout_7->setObjectName(QString::fromUtf8("verticalLayout_7"));
        scrollArea = new QScrollArea(groupBox_9);
        scrollArea->setObjectName(QString::fromUtf8("scrollArea"));
        scrollArea->setWidgetResizable(true);
        scrollAreaWidgetContents = new QWidget();
        scrollAreaWidgetContents->setObjectName(QString::fromUtf8("scrollAreaWidgetContents"));
        scrollAreaWidgetContents->setGeometry(QRect(0, -36, 381, 565));
        gridLayout_4 = new QGridLayout(scrollAreaWidgetContents);
        gridLayout_4->setObjectName(QString::fromUtf8("gridLayout_4"));
        condenserApertureSpinBox = new QSpinBox(scrollAreaWidgetContents);
        condenserApertureSpinBox->setObjectName(QString::fromUtf8("condenserApertureSpinBox"));
        condenserApertureSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(condenserApertureSpinBox->sizePolicy().hasHeightForWidth());
        condenserApertureSpinBox->setSizePolicy(sizePolicy3);

        gridLayout_4->addWidget(condenserApertureSpinBox, 7, 1, 1, 1);

        acquisitionDateCheckBox = new QCheckBox(scrollAreaWidgetContents);
        acquisitionDateCheckBox->setObjectName(QString::fromUtf8("acquisitionDateCheckBox"));

        gridLayout_4->addWidget(acquisitionDateCheckBox, 11, 0, 1, 1);

        highTensionSpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        highTensionSpinBox->setObjectName(QString::fromUtf8("highTensionSpinBox"));
        highTensionSpinBox->setEnabled(true);
        sizePolicy3.setHeightForWidth(highTensionSpinBox->sizePolicy().hasHeightForWidth());
        highTensionSpinBox->setSizePolicy(sizePolicy3);
        highTensionSpinBox->setDecimals(0);
        highTensionSpinBox->setMinimum(0.000000000000000);
        highTensionSpinBox->setMaximum(300.000000000000000);
        highTensionSpinBox->setSingleStep(10.000000000000000);
        highTensionSpinBox->setValue(200.000000000000000);

        gridLayout_4->addWidget(highTensionSpinBox, 0, 1, 1, 1);

        cameraCheckBox = new QCheckBox(scrollAreaWidgetContents);
        cameraCheckBox->setObjectName(QString::fromUtf8("cameraCheckBox"));
        cameraCheckBox->setChecked(true);

        gridLayout_4->addWidget(cameraCheckBox, 12, 0, 1, 1);

        microscopeComboBox = new QComboBox(scrollAreaWidgetContents);
        microscopeComboBox->addItem(QString());
        microscopeComboBox->addItem(QString());
        microscopeComboBox->addItem(QString());
        microscopeComboBox->setObjectName(QString::fromUtf8("microscopeComboBox"));
        microscopeComboBox->setEnabled(true);

        gridLayout_4->addWidget(microscopeComboBox, 13, 1, 1, 1);

        modeSelector = new QComboBox(scrollAreaWidgetContents);
        modeSelector->addItem(QString());
        modeSelector->addItem(QString());
        modeSelector->addItem(QString());
        modeSelector->addItem(QString());
        modeSelector->addItem(QString());
        modeSelector->setObjectName(QString::fromUtf8("modeSelector"));
        modeSelector->setEnabled(false);
        sizePolicy3.setHeightForWidth(modeSelector->sizePolicy().hasHeightForWidth());
        modeSelector->setSizePolicy(sizePolicy3);

        gridLayout_4->addWidget(modeSelector, 3, 1, 1, 1);

        label_25 = new QLabel(scrollAreaWidgetContents);
        label_25->setObjectName(QString::fromUtf8("label_25"));
        QSizePolicy sizePolicy8(QSizePolicy::Fixed, QSizePolicy::Maximum);
        sizePolicy8.setHorizontalStretch(0);
        sizePolicy8.setVerticalStretch(0);
        sizePolicy8.setHeightForWidth(label_25->sizePolicy().hasHeightForWidth());
        label_25->setSizePolicy(sizePolicy8);

        gridLayout_4->addWidget(label_25, 9, 2, 1, 1);

        spotCheckBox = new QCheckBox(scrollAreaWidgetContents);
        spotCheckBox->setObjectName(QString::fromUtf8("spotCheckBox"));

        gridLayout_4->addWidget(spotCheckBox, 5, 0, 1, 1);

        cameraLengthCheckBox = new QCheckBox(scrollAreaWidgetContents);
        cameraLengthCheckBox->setObjectName(QString::fromUtf8("cameraLengthCheckBox"));

        gridLayout_4->addWidget(cameraLengthCheckBox, 2, 0, 1, 1);

        modeCheckBox = new QCheckBox(scrollAreaWidgetContents);
        modeCheckBox->setObjectName(QString::fromUtf8("modeCheckBox"));

        gridLayout_4->addWidget(modeCheckBox, 3, 0, 1, 1);

        acquisitionDate = new QDateEdit(scrollAreaWidgetContents);
        acquisitionDate->setObjectName(QString::fromUtf8("acquisitionDate"));
        acquisitionDate->setEnabled(false);
        sizePolicy3.setHeightForWidth(acquisitionDate->sizePolicy().hasHeightForWidth());
        acquisitionDate->setSizePolicy(sizePolicy3);
        acquisitionDate->setDate(QDate(2020, 1, 1));

        gridLayout_4->addWidget(acquisitionDate, 11, 1, 1, 1);

        magnificationSpinBox = new QSpinBox(scrollAreaWidgetContents);
        magnificationSpinBox->setObjectName(QString::fromUtf8("magnificationSpinBox"));
        magnificationSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(magnificationSpinBox->sizePolicy().hasHeightForWidth());
        magnificationSpinBox->setSizePolicy(sizePolicy3);
        magnificationSpinBox->setMinimum(0);
        magnificationSpinBox->setMaximum(2000000);
        magnificationSpinBox->setSingleStep(1000);
        magnificationSpinBox->setValue(0);

        gridLayout_4->addWidget(magnificationSpinBox, 1, 1, 1, 1);

        cameraComboBox = new QComboBox(scrollAreaWidgetContents);
        cameraComboBox->addItem(QString());
        cameraComboBox->addItem(QString());
        cameraComboBox->setObjectName(QString::fromUtf8("cameraComboBox"));
        cameraComboBox->setEnabled(true);

        gridLayout_4->addWidget(cameraComboBox, 12, 1, 1, 1);

        label_21 = new QLabel(scrollAreaWidgetContents);
        label_21->setObjectName(QString::fromUtf8("label_21"));
        sizePolicy1.setHeightForWidth(label_21->sizePolicy().hasHeightForWidth());
        label_21->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_21, 0, 2, 1, 1);

        convergenceAngleSpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        convergenceAngleSpinBox->setObjectName(QString::fromUtf8("convergenceAngleSpinBox"));
        convergenceAngleSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(convergenceAngleSpinBox->sizePolicy().hasHeightForWidth());
        convergenceAngleSpinBox->setSizePolicy(sizePolicy3);
        convergenceAngleSpinBox->setMinimum(0.000000000000000);
        convergenceAngleSpinBox->setValue(0.000000000000000);

        gridLayout_4->addWidget(convergenceAngleSpinBox, 8, 1, 1, 1);

        precessionFrequencyCheckBox = new QCheckBox(scrollAreaWidgetContents);
        precessionFrequencyCheckBox->setObjectName(QString::fromUtf8("precessionFrequencyCheckBox"));

        gridLayout_4->addWidget(precessionFrequencyCheckBox, 9, 0, 1, 1);

        alphaCheckBox = new QCheckBox(scrollAreaWidgetContents);
        alphaCheckBox->setObjectName(QString::fromUtf8("alphaCheckBox"));

        gridLayout_4->addWidget(alphaCheckBox, 4, 0, 1, 1);

        microscopeCheckBox = new QCheckBox(scrollAreaWidgetContents);
        microscopeCheckBox->setObjectName(QString::fromUtf8("microscopeCheckBox"));
        microscopeCheckBox->setChecked(true);

        gridLayout_4->addWidget(microscopeCheckBox, 13, 0, 1, 1);

        spotSpinBox = new QSpinBox(scrollAreaWidgetContents);
        spotSpinBox->setObjectName(QString::fromUtf8("spotSpinBox"));
        spotSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(spotSpinBox->sizePolicy().hasHeightForWidth());
        spotSpinBox->setSizePolicy(sizePolicy3);
        spotSpinBox->setMinimum(1);
        spotSpinBox->setMaximum(3);

        gridLayout_4->addWidget(spotSpinBox, 5, 1, 1, 1);

        spotSizeSpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        spotSizeSpinBox->setObjectName(QString::fromUtf8("spotSizeSpinBox"));
        spotSizeSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(spotSizeSpinBox->sizePolicy().hasHeightForWidth());
        spotSizeSpinBox->setSizePolicy(sizePolicy3);
        spotSizeSpinBox->setSingleStep(0.100000000000000);

        gridLayout_4->addWidget(spotSizeSpinBox, 6, 1, 1, 1);

        alphaSpinBox = new QSpinBox(scrollAreaWidgetContents);
        alphaSpinBox->setObjectName(QString::fromUtf8("alphaSpinBox"));
        alphaSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(alphaSpinBox->sizePolicy().hasHeightForWidth());
        alphaSpinBox->setSizePolicy(sizePolicy3);
        alphaSpinBox->setMinimum(1);
        alphaSpinBox->setMaximum(5);
        alphaSpinBox->setValue(3);

        gridLayout_4->addWidget(alphaSpinBox, 4, 1, 1, 1);

        label_23 = new QLabel(scrollAreaWidgetContents);
        label_23->setObjectName(QString::fromUtf8("label_23"));
        sizePolicy1.setHeightForWidth(label_23->sizePolicy().hasHeightForWidth());
        label_23->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_23, 8, 2, 1, 1);

        label_20 = new QLabel(scrollAreaWidgetContents);
        label_20->setObjectName(QString::fromUtf8("label_20"));
        sizePolicy1.setHeightForWidth(label_20->sizePolicy().hasHeightForWidth());
        label_20->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_20, 7, 2, 1, 1);

        highTensionCheckBox = new QCheckBox(scrollAreaWidgetContents);
        highTensionCheckBox->setObjectName(QString::fromUtf8("highTensionCheckBox"));
        highTensionCheckBox->setEnabled(true);
        sizePolicy.setHeightForWidth(highTensionCheckBox->sizePolicy().hasHeightForWidth());
        highTensionCheckBox->setSizePolicy(sizePolicy);
        highTensionCheckBox->setChecked(true);

        gridLayout_4->addWidget(highTensionCheckBox, 0, 0, 1, 1);

        cameraLengthSpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        cameraLengthSpinBox->setObjectName(QString::fromUtf8("cameraLengthSpinBox"));
        cameraLengthSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(cameraLengthSpinBox->sizePolicy().hasHeightForWidth());
        cameraLengthSpinBox->setSizePolicy(sizePolicy3);
        cameraLengthSpinBox->setDecimals(1);
        cameraLengthSpinBox->setMinimum(0.000000000000000);
        cameraLengthSpinBox->setMaximum(999.000000000000000);
        cameraLengthSpinBox->setValue(8.000000000000000);

        gridLayout_4->addWidget(cameraLengthSpinBox, 2, 1, 1, 1);

        label_19 = new QLabel(scrollAreaWidgetContents);
        label_19->setObjectName(QString::fromUtf8("label_19"));
        sizePolicy1.setHeightForWidth(label_19->sizePolicy().hasHeightForWidth());
        label_19->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_19, 10, 2, 1, 1);

        label_24 = new QLabel(scrollAreaWidgetContents);
        label_24->setObjectName(QString::fromUtf8("label_24"));
        sizePolicy1.setHeightForWidth(label_24->sizePolicy().hasHeightForWidth());
        label_24->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_24, 6, 2, 1, 1);

        convergenceAngleCheckBox = new QCheckBox(scrollAreaWidgetContents);
        convergenceAngleCheckBox->setObjectName(QString::fromUtf8("convergenceAngleCheckBox"));

        gridLayout_4->addWidget(convergenceAngleCheckBox, 8, 0, 1, 1);

        magnificationCheckBox = new QCheckBox(scrollAreaWidgetContents);
        magnificationCheckBox->setObjectName(QString::fromUtf8("magnificationCheckBox"));

        gridLayout_4->addWidget(magnificationCheckBox, 1, 0, 1, 1);

        magnificationSelector = new QComboBox(scrollAreaWidgetContents);
        magnificationSelector->addItem(QString());
        magnificationSelector->addItem(QString());
        magnificationSelector->setObjectName(QString::fromUtf8("magnificationSelector"));
        magnificationSelector->setEnabled(false);
        sizePolicy.setHeightForWidth(magnificationSelector->sizePolicy().hasHeightForWidth());
        magnificationSelector->setSizePolicy(sizePolicy);

        gridLayout_4->addWidget(magnificationSelector, 1, 2, 1, 1);

        precessionFrequencySpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        precessionFrequencySpinBox->setObjectName(QString::fromUtf8("precessionFrequencySpinBox"));
        precessionFrequencySpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(precessionFrequencySpinBox->sizePolicy().hasHeightForWidth());
        precessionFrequencySpinBox->setSizePolicy(sizePolicy3);
        precessionFrequencySpinBox->setDecimals(0);
        precessionFrequencySpinBox->setMinimum(0.000000000000000);
        precessionFrequencySpinBox->setMaximum(1000.000000000000000);
        precessionFrequencySpinBox->setValue(100.000000000000000);

        gridLayout_4->addWidget(precessionFrequencySpinBox, 9, 1, 1, 1);

        precessionAngleSpinBox = new QDoubleSpinBox(scrollAreaWidgetContents);
        precessionAngleSpinBox->setObjectName(QString::fromUtf8("precessionAngleSpinBox"));
        precessionAngleSpinBox->setEnabled(false);
        sizePolicy3.setHeightForWidth(precessionAngleSpinBox->sizePolicy().hasHeightForWidth());
        precessionAngleSpinBox->setSizePolicy(sizePolicy3);
        precessionAngleSpinBox->setMinimum(0.000000000000000);
        precessionAngleSpinBox->setMaximum(10.000000000000000);
        precessionAngleSpinBox->setSingleStep(0.100000000000000);
        precessionAngleSpinBox->setValue(1.000000000000000);

        gridLayout_4->addWidget(precessionAngleSpinBox, 10, 1, 1, 1);

        spotSizeCheckBox = new QCheckBox(scrollAreaWidgetContents);
        spotSizeCheckBox->setObjectName(QString::fromUtf8("spotSizeCheckBox"));

        gridLayout_4->addWidget(spotSizeCheckBox, 6, 0, 1, 1);

        condenserApertureCheckBox = new QCheckBox(scrollAreaWidgetContents);
        condenserApertureCheckBox->setObjectName(QString::fromUtf8("condenserApertureCheckBox"));

        gridLayout_4->addWidget(condenserApertureCheckBox, 7, 0, 1, 1);

        precessionAngleCheckBox = new QCheckBox(scrollAreaWidgetContents);
        precessionAngleCheckBox->setObjectName(QString::fromUtf8("precessionAngleCheckBox"));

        gridLayout_4->addWidget(precessionAngleCheckBox, 10, 0, 1, 1);

        label_22 = new QLabel(scrollAreaWidgetContents);
        label_22->setObjectName(QString::fromUtf8("label_22"));
        sizePolicy1.setHeightForWidth(label_22->sizePolicy().hasHeightForWidth());
        label_22->setSizePolicy(sizePolicy1);

        gridLayout_4->addWidget(label_22, 2, 2, 1, 1);

        stepGroupBox = new QGroupBox(scrollAreaWidgetContents);
        stepGroupBox->setObjectName(QString::fromUtf8("stepGroupBox"));
        sizePolicy1.setHeightForWidth(stepGroupBox->sizePolicy().hasHeightForWidth());
        stepGroupBox->setSizePolicy(sizePolicy1);
        stepGroupBox->setCheckable(true);
        stepGroupBox->setChecked(false);
        gridLayout_5 = new QGridLayout(stepGroupBox);
        gridLayout_5->setObjectName(QString::fromUtf8("gridLayout_5"));
        stepYSpinBox = new QDoubleSpinBox(stepGroupBox);
        stepYSpinBox->setObjectName(QString::fromUtf8("stepYSpinBox"));
        stepYSpinBox->setSingleStep(0.100000000000000);

        gridLayout_5->addWidget(stepYSpinBox, 1, 1, 1, 1);

        stepXSpinBox = new QDoubleSpinBox(stepGroupBox);
        stepXSpinBox->setObjectName(QString::fromUtf8("stepXSpinBox"));
        stepXSpinBox->setSingleStep(0.100000000000000);

        gridLayout_5->addWidget(stepXSpinBox, 0, 1, 1, 1);

        label_29 = new QLabel(stepGroupBox);
        label_29->setObjectName(QString::fromUtf8("label_29"));
        sizePolicy1.setHeightForWidth(label_29->sizePolicy().hasHeightForWidth());
        label_29->setSizePolicy(sizePolicy1);

        gridLayout_5->addWidget(label_29, 0, 0, 1, 1);

        label_28 = new QLabel(stepGroupBox);
        label_28->setObjectName(QString::fromUtf8("label_28"));

        gridLayout_5->addWidget(label_28, 1, 0, 1, 1);

        label_26 = new QLabel(stepGroupBox);
        label_26->setObjectName(QString::fromUtf8("label_26"));

        gridLayout_5->addWidget(label_26, 0, 2, 1, 1);

        label_27 = new QLabel(stepGroupBox);
        label_27->setObjectName(QString::fromUtf8("label_27"));

        gridLayout_5->addWidget(label_27, 1, 2, 1, 1);


        gridLayout_4->addWidget(stepGroupBox, 14, 0, 1, 1);

        scrollArea->setWidget(scrollAreaWidgetContents);

        verticalLayout_7->addWidget(scrollArea);


        horizontalLayout_6->addWidget(groupBox_9);

        groupBox_8 = new QGroupBox(centralwidget);
        groupBox_8->setObjectName(QString::fromUtf8("groupBox_8"));
        verticalLayout_6 = new QVBoxLayout(groupBox_8);
        verticalLayout_6->setObjectName(QString::fromUtf8("verticalLayout_6"));
        tableView = new QTableView(groupBox_8);
        tableView->setObjectName(QString::fromUtf8("tableView"));
        QSizePolicy sizePolicy9(QSizePolicy::Preferred, QSizePolicy::Expanding);
        sizePolicy9.setHorizontalStretch(0);
        sizePolicy9.setVerticalStretch(0);
        sizePolicy9.setHeightForWidth(tableView->sizePolicy().hasHeightForWidth());
        tableView->setSizePolicy(sizePolicy9);
        tableView->setMinimumSize(QSize(450, 0));

        verticalLayout_6->addWidget(tableView);


        horizontalLayout_6->addWidget(groupBox_8);


        verticalLayout_8->addLayout(horizontalLayout_6);

        applyCalibrationButton = new QPushButton(centralwidget);
        applyCalibrationButton->setObjectName(QString::fromUtf8("applyCalibrationButton"));

        verticalLayout_8->addWidget(applyCalibrationButton);

        groupBox_7 = new QGroupBox(centralwidget);
        groupBox_7->setObjectName(QString::fromUtf8("groupBox_7"));
        verticalLayout_5 = new QVBoxLayout(groupBox_7);
        verticalLayout_5->setObjectName(QString::fromUtf8("verticalLayout_5"));
        horizontalLayout_5 = new QHBoxLayout();
        horizontalLayout_5->setObjectName(QString::fromUtf8("horizontalLayout_5"));
        label_16 = new QLabel(groupBox_7);
        label_16->setObjectName(QString::fromUtf8("label_16"));

        horizontalLayout_5->addWidget(label_16);

        calibrationPathLineEdit = new QLineEdit(groupBox_7);
        calibrationPathLineEdit->setObjectName(QString::fromUtf8("calibrationPathLineEdit"));

        horizontalLayout_5->addWidget(calibrationPathLineEdit);

        browseCalibrationFileButton = new QPushButton(groupBox_7);
        browseCalibrationFileButton->setObjectName(QString::fromUtf8("browseCalibrationFileButton"));

        horizontalLayout_5->addWidget(browseCalibrationFileButton);


        verticalLayout_5->addLayout(horizontalLayout_5);

        showCalibrationsButton = new QPushButton(groupBox_7);
        showCalibrationsButton->setObjectName(QString::fromUtf8("showCalibrationsButton"));
        sizePolicy.setHeightForWidth(showCalibrationsButton->sizePolicy().hasHeightForWidth());
        showCalibrationsButton->setSizePolicy(sizePolicy);

        verticalLayout_5->addWidget(showCalibrationsButton);


        verticalLayout_8->addWidget(groupBox_7);


        verticalLayout_25->addLayout(verticalLayout_8);


        horizontalLayout_14->addLayout(verticalLayout_25);


        verticalLayout_26->addLayout(horizontalLayout_14);

        horizontalLayout_8 = new QHBoxLayout();
        horizontalLayout_8->setObjectName(QString::fromUtf8("horizontalLayout_8"));
        printConverterButton = new QPushButton(centralwidget);
        printConverterButton->setObjectName(QString::fromUtf8("printConverterButton"));
        sizePolicy.setHeightForWidth(printConverterButton->sizePolicy().hasHeightForWidth());
        printConverterButton->setSizePolicy(sizePolicy);

        horizontalLayout_8->addWidget(printConverterButton);

        refreshButton = new QPushButton(centralwidget);
        refreshButton->setObjectName(QString::fromUtf8("refreshButton"));
        sizePolicy.setHeightForWidth(refreshButton->sizePolicy().hasHeightForWidth());
        refreshButton->setSizePolicy(sizePolicy);

        horizontalLayout_8->addWidget(refreshButton);

        horizontalSpacer_2 = new QSpacerItem(40, 20, QSizePolicy::Expanding, QSizePolicy::Minimum);

        horizontalLayout_8->addItem(horizontalSpacer_2);


        verticalLayout_26->addLayout(horizontalLayout_8);

        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName(QString::fromUtf8("menubar"));
        menubar->setGeometry(QRect(0, 0, 1735, 22));
        menuFile = new QMenu(menubar);
        menuFile->setObjectName(QString::fromUtf8("menuFile"));
        menuPlot = new QMenu(menubar);
        menuPlot->setObjectName(QString::fromUtf8("menuPlot"));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName(QString::fromUtf8("statusbar"));
        MainWindow->setStatusBar(statusbar);

        menubar->addAction(menuFile->menuAction());
        menubar->addAction(menuPlot->menuAction());
        menuFile->addAction(actionExit);
        menuFile->addAction(actionOpen);
        menuFile->addAction(actionClose);
        menuPlot->addAction(actionVBF);
        menuPlot->addAction(actionFrames);

        retranslateUi(MainWindow);

        tabWidget_2->setCurrentIndex(0);
        tabWidget->setCurrentIndex(0);
        microscopeComboBox->setCurrentIndex(1);


        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "MainWindow", nullptr));
        actionVBF->setText(QApplication::translate("MainWindow", "VBF", nullptr));
        actionFrames->setText(QApplication::translate("MainWindow", "Frames", nullptr));
        actionExit->setText(QApplication::translate("MainWindow", "Exit", nullptr));
        actionOpen->setText(QApplication::translate("MainWindow", "Open", nullptr));
        actionClose->setText(QApplication::translate("MainWindow", "Close", nullptr));
        label->setText(QApplication::translate("MainWindow", "Data path:", nullptr));
        browseDataButton->setText(QApplication::translate("MainWindow", "Browse", nullptr));
        loadButton->setText(QApplication::translate("MainWindow", "Load", nullptr));
        resetButton->setText(QApplication::translate("MainWindow", "Reset", nullptr));
        label_2->setText(QApplication::translate("MainWindow", "Loaded signal:", nullptr));
        signalLabel->setText(QApplication::translate("MainWindow", "None", nullptr));
        groupBox->setTitle(QApplication::translate("MainWindow", "StackShape", nullptr));
        label_4->setText(QApplication::translate("MainWindow", "Frames:", nullptr));
        framesLabel->setText(QApplication::translate("MainWindow", "None", nullptr));
        label_6->setText(QApplication::translate("MainWindow", "X", nullptr));
        label_7->setText(QApplication::translate("MainWindow", "Y", nullptr));
        reshapeButton->setText(QApplication::translate("MainWindow", "Reshape", nullptr));
        groupBox_2->setTitle(QApplication::translate("MainWindow", "Chunking", nullptr));
        label_8->setText(QApplication::translate("MainWindow", "Chunks:", nullptr));
        chunksLabel->setText(QApplication::translate("MainWindow", "None", nullptr));
        label_10->setText(QApplication::translate("MainWindow", "Chunksize:", nullptr));
        label_36->setText(QApplication::translate("MainWindow", "ky", nullptr));
        label_14->setText(QApplication::translate("MainWindow", "y", nullptr));
        label_35->setText(QApplication::translate("MainWindow", "kx", nullptr));
        label_12->setText(QApplication::translate("MainWindow", "x", nullptr));
        rechunkButton->setText(QApplication::translate("MainWindow", "Rechunk", nullptr));
        groupBox_3->setTitle(QApplication::translate("MainWindow", "Datatype", nullptr));
        readDataInfoButton->setText(QApplication::translate("MainWindow", "Read", nullptr));
        label_11->setText(QApplication::translate("MainWindow", "dtype:", nullptr));
        dtypeLabel->setText(QApplication::translate("MainWindow", "None", nullptr));
        maxValueLabel->setText(QApplication::translate("MainWindow", "None", nullptr));
        label_13->setText(QApplication::translate("MainWindow", "Maxvalue", nullptr));
        label_15->setText(QApplication::translate("MainWindow", "New dtype:", nullptr));
        dtypeComboBox->setItemText(0, QApplication::translate("MainWindow", "bool", nullptr));
        dtypeComboBox->setItemText(1, QApplication::translate("MainWindow", "uint8", nullptr));
        dtypeComboBox->setItemText(2, QApplication::translate("MainWindow", "uint16", nullptr));
        dtypeComboBox->setItemText(3, QApplication::translate("MainWindow", "uint32", nullptr));

        changeDtypeButton->setText(QApplication::translate("MainWindow", "Apply", nullptr));
        label_34->setText(QApplication::translate("MainWindow", "Specimen", nullptr));
        label_33->setText(QApplication::translate("MainWindow", "Operator", nullptr));
        tabWidget_2->setTabText(tabWidget_2->indexOf(tab_6), QApplication::translate("MainWindow", "Session", nullptr));
        label_30->setText(QApplication::translate("MainWindow", "Z [um]", nullptr));
        label_18->setText(QApplication::translate("MainWindow", "Y [um]", nullptr));
        label_17->setText(QApplication::translate("MainWindow", "X [um]", nullptr));
        label_32->setText(QApplication::translate("MainWindow", "Tilt Y / Rot [deg]", nullptr));
        label_31->setText(QApplication::translate("MainWindow", "Tilt X [deg]", nullptr));
        rotationHolderCheckBox->setText(QApplication::translate("MainWindow", "Rotation holder", nullptr));
        tabWidget_2->setTabText(tabWidget_2->indexOf(tab_4), QApplication::translate("MainWindow", "Stage", nullptr));
        tabWidget_2->setTabText(tabWidget_2->indexOf(tab_5), QApplication::translate("MainWindow", "Notes", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tab), QApplication::translate("MainWindow", "Current axes manager", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tab_2), QApplication::translate("MainWindow", "Current metadata", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(tab_3), QApplication::translate("MainWindow", "Current original metadata", nullptr));
        groupBox_4->setTitle(QApplication::translate("MainWindow", "Conversion", nullptr));
        writeButton->setText(QApplication::translate("MainWindow", "Write", nullptr));
        overwriteCheckBox->setText(QApplication::translate("MainWindow", "Overwrite", nullptr));
        VBFGroupBox->setTitle(QApplication::translate("MainWindow", "VBF", nullptr));
        label_3->setText(QApplication::translate("MainWindow", "X", nullptr));
        label_9->setText(QApplication::translate("MainWindow", "Width", nullptr));
        label_5->setText(QApplication::translate("MainWindow", "Y", nullptr));
        fileFormatGroupBox->setTitle(QApplication::translate("MainWindow", "File formats", nullptr));
        hspyCheckBox->setText(QApplication::translate("MainWindow", ".hspy", nullptr));
        hdfCheckBox->setText(QApplication::translate("MainWindow", ".hdf5", nullptr));
        jpgCheckBox->setText(QApplication::translate("MainWindow", ".jpg", nullptr));
        pngCheckBox->setText(QApplication::translate("MainWindow", ".png", nullptr));
        tifCheckBox->setText(QApplication::translate("MainWindow", ".tif", nullptr));
        groupBox_9->setTitle(QApplication::translate("MainWindow", "Nominal acquisition parameters", nullptr));
        acquisitionDateCheckBox->setText(QApplication::translate("MainWindow", "Acquisition Date", nullptr));
        cameraCheckBox->setText(QApplication::translate("MainWindow", "Camera", nullptr));
        microscopeComboBox->setItemText(0, QApplication::translate("MainWindow", "ARM200F", nullptr));
        microscopeComboBox->setItemText(1, QApplication::translate("MainWindow", "2100F", nullptr));
        microscopeComboBox->setItemText(2, QApplication::translate("MainWindow", "2100", nullptr));

        modeSelector->setItemText(0, QApplication::translate("MainWindow", "None", nullptr));
        modeSelector->setItemText(1, QApplication::translate("MainWindow", "STEM", nullptr));
        modeSelector->setItemText(2, QApplication::translate("MainWindow", "TEM", nullptr));
        modeSelector->setItemText(3, QApplication::translate("MainWindow", "NBD", nullptr));
        modeSelector->setItemText(4, QApplication::translate("MainWindow", "CBD", nullptr));

        label_25->setText(QApplication::translate("MainWindow", "Hz", nullptr));
        spotCheckBox->setText(QApplication::translate("MainWindow", "Spot", nullptr));
        cameraLengthCheckBox->setText(QApplication::translate("MainWindow", "Cameralength", nullptr));
        modeCheckBox->setText(QApplication::translate("MainWindow", "Mode", nullptr));
        cameraComboBox->setItemText(0, QApplication::translate("MainWindow", "Merlin", nullptr));
        cameraComboBox->setItemText(1, QApplication::translate("MainWindow", "US1000 1", nullptr));

        label_21->setText(QApplication::translate("MainWindow", "keV", nullptr));
        precessionFrequencyCheckBox->setText(QApplication::translate("MainWindow", "Rocking Frequency", nullptr));
        alphaCheckBox->setText(QApplication::translate("MainWindow", "Alpha", nullptr));
        microscopeCheckBox->setText(QApplication::translate("MainWindow", "Microscope", nullptr));
        label_23->setText(QApplication::translate("MainWindow", "mrad", nullptr));
        label_20->setText(QApplication::translate("MainWindow", "um", nullptr));
        highTensionCheckBox->setText(QApplication::translate("MainWindow", "High Tension", nullptr));
        label_19->setText(QApplication::translate("MainWindow", "deg", nullptr));
        label_24->setText(QApplication::translate("MainWindow", "nm", nullptr));
        convergenceAngleCheckBox->setText(QApplication::translate("MainWindow", "Convergence Angle", nullptr));
        magnificationCheckBox->setText(QApplication::translate("MainWindow", "Magnification", nullptr));
        magnificationSelector->setItemText(0, QApplication::translate("MainWindow", "MAG1", nullptr));
        magnificationSelector->setItemText(1, QApplication::translate("MainWindow", "SAMAG", nullptr));

        spotSizeCheckBox->setText(QApplication::translate("MainWindow", "Spotsize", nullptr));
        condenserApertureCheckBox->setText(QApplication::translate("MainWindow", "Condenser Aperture", nullptr));
        precessionAngleCheckBox->setText(QApplication::translate("MainWindow", "Rocking Angle", nullptr));
        label_22->setText(QApplication::translate("MainWindow", "cm", nullptr));
        stepGroupBox->setTitle(QApplication::translate("MainWindow", "Scan step", nullptr));
        label_29->setText(QApplication::translate("MainWindow", "X", nullptr));
        label_28->setText(QApplication::translate("MainWindow", "Y", nullptr));
        label_26->setText(QApplication::translate("MainWindow", "nm", nullptr));
        label_27->setText(QApplication::translate("MainWindow", "nm", nullptr));
        groupBox_8->setTitle(QApplication::translate("MainWindow", "Acquisition parameter view", nullptr));
        applyCalibrationButton->setText(QApplication::translate("MainWindow", "Apply calibration", nullptr));
        groupBox_7->setTitle(QApplication::translate("MainWindow", "Calibration table", nullptr));
        label_16->setText(QApplication::translate("MainWindow", "Path:", nullptr));
        calibrationPathLineEdit->setText(QString());
        browseCalibrationFileButton->setText(QApplication::translate("MainWindow", "Browse", nullptr));
        showCalibrationsButton->setText(QApplication::translate("MainWindow", "Show", nullptr));
        printConverterButton->setText(QApplication::translate("MainWindow", "Print Converter", nullptr));
        refreshButton->setText(QApplication::translate("MainWindow", "Refresh GUI", nullptr));
        menuFile->setTitle(QApplication::translate("MainWindow", "File", nullptr));
        menuPlot->setTitle(QApplication::translate("MainWindow", "Plot", nullptr));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_STACK_CONVERTER_H
