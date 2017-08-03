#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QFileInfo>

void callbackPlaybackStopped(void * p)
{
    MainWindow *w = (MainWindow*)p;
    w->callbackProcessingStopped();
}


MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    processingStopped(false),
    playSpeed(1),
    fallState(NONE),
    timeWindowSize(50000),
    maxSpeed(5),
    minSpeed(0.05),
    incSpeed(0.2)
{
    ui->setupUi(this);

    QStringList args = QCoreApplication::arguments();
    if(args.size() != 2) {
        exit(1);
    }

    QString fileName = args.at(1);
    QFileInfo fileInfo(fileName);

    labelFileName = fileInfo.path() + "/" + fileInfo.baseName() + QString(".label");
    qDebug("File: %s", labelFileName.toLocal8Bit().data());
    ui->l_filename->setText(labelFileName);
    timer = new QTimer(this);
    connect(timer,SIGNAL(timeout()),this,SLOT(redrawUI()));
    connect(ui->b_restart,SIGNAL(clicked()),this,SLOT(onClickRestart()));
    connect(ui->b_cancel,SIGNAL(clicked()),this,SLOT(onClickCancel()));
    connect(ui->b_finish,SIGNAL(clicked()),this,SLOT(onClickFinish()));

    camHandler.setDVSEventReciever(this);
    camHandler.setFrameReciever(this);

    onClickRestart();
}

void MainWindow::newEvent(const sDVSEventDepacked & event)
{
    {
        QMutexLocker locker(&m_queueMutex);
        m_eventQueue.push(event);
    }
}

void MainWindow::newFrame(const caerFrameEvent &frame)
{
    {
        QMutexLocker locker(&m_frameMutex);
        // Convert to qt image
        u_int16_t* inPtr = frame->pixels;
        for(int y = 0; y < m_sy; y++) {
            uchar* line = m_currFrame.scanLine(y);
            for(int x = 0; x < m_sx; x++) {
                *line++ = inPtr[y*m_sx + x]>>8;
                *line++ = inPtr[y*m_sx + x]>>8;
                *line++ = inPtr[y*m_sx + x]>>8;
            }
        }
    }
}

void MainWindow::redrawUI()
{
    if(m_eventQueue.size()>0) {
        QMutexLocker locker(&m_queueMutex);
        m_eventBuffer.addEvents(m_eventQueue);
    }

    int time = m_eventBuffer.getCurrTime();
    int evCnt = m_eventBuffer.getSize();
    QImage bufferImg = m_currFrame.copy();

    auto & buff = m_eventBuffer.getLockedBuffer();
    for(sDVSEventDepacked & e:buff) {
        uchar* line = bufferImg.scanLine(e.y);
        uchar* px = line + 3*e.x;

        if(e.pol) {
            *px++ = 255*(1 - 0.8*((float)time - e.ts)/timeWindowSize);
            *px++ = 0;
            *px++ = 0;
        } else {
            *px++ = 0;
            *px++ = 255*(1 - 0.8*((float)time - e.ts)/timeWindowSize);
            *px++ = 0;
        }
    }
    m_eventBuffer.releaseLockedBuffer();

    ui->l_video->setPixmap(QPixmap::fromImage(bufferImg));

    ui->l_status->setText(QString("Events: %1 Time: %2 Playspeed: %3 State: %4").arg(evCnt).arg(time).arg(playSpeed).arg(fallState));
}
void MainWindow::onClickRestart()
{
    processingStopped = false;
    playSpeed=1;
    fallState=NONE;

    QStringList args = QCoreApplication::arguments();
    QString fileName = args.at(1);
    camHandler.connect(fileName,callbackPlaybackStopped,this);

    m_sx = camHandler.getFrameSize().x();
    m_sy = camHandler.getFrameSize().y();
    m_currFrame = QImage(m_sx,m_sy,QImage::Format_RGB888);

    m_eventBuffer.setup(timeWindowSize,m_sx,m_sy);
    fallLabelFile.close();
    fallLabelFile.open(labelFileName.toStdString(),std::fstream::out);
    if(!fallLabelFile.is_open()) {
        qDebug("Failed to open output file: %s",strerror(errno));
        exit(1);
    }

    timer->start(30);

    camHandler.startStreaming();
}
void MainWindow::onClickCancel()
{
    fallLabelFile.close();
    QFile::remove(labelFileName);
    QCoreApplication::exit(1);
}
void MainWindow::onClickFinish()
{
    fallLabelFile.close();
    QCoreApplication::exit(0);
}

void MainWindow::keyPressEvent(QKeyEvent *e)
{
    int time;
    switch (e->key()) {
    case Qt::Key_Plus:
        playSpeed =qMin(playSpeed + incSpeed,maxSpeed);
        camHandler.changePlaybackSpeed(playSpeed);
        break;
    case Qt::Key_Minus:
        playSpeed =qMax(playSpeed - incSpeed,minSpeed);
        camHandler.changePlaybackSpeed(playSpeed);
        break;
    case Qt::Key_A: {
        switch (fallState) {
        case NONE:
            fallState = FALLING;
            time = m_eventBuffer.getCurrTime();
            fallLabelFile << time << ";";
            break;
        case FALLING: {
            fallState = FALLING_DONE;
            time = m_eventBuffer.getCurrTime();
            fallLabelFile << time << ";";

            int i = -1;
            QString fileName;

            do {
                i++;
                fileName = QString("fall%1.png").arg(i);
            } while(QFile(fileName).exists());
            if(!m_currFrame.save(fileName)) {
                qDebug("Can't save file %s!\n", fileName.toStdString().c_str());
                QCoreApplication::exit(1);
            }
        }

        break;
        case FALLING_DONE:
            time = m_eventBuffer.getCurrTime();
            fallState = GETTIN_UP;
            fallLabelFile << time << ";";
            break;
        case GETTIN_UP:
            fallState = NONE;
            time = m_eventBuffer.getCurrTime();
            fallLabelFile << time;
            fallLabelFile << std::endl;
            break;
        }
        break;
    }
    case Qt::Key_Y: {
        QMutexLocker locker(&m_frameMutex);
        int i = -1;
        QString fileName;

        do {
            i++;
            fileName = QString("screenshot%1.png").arg(i);
        } while(QFile(fileName).exists());

        if(!m_currFrame.save(fileName)) {
            qDebug("Can't save file %s!\n", fileName.toStdString().c_str());
            QCoreApplication::exit(1);
        }

    }
    }
}

MainWindow::~MainWindow()
{
    camHandler.disconnect();
    delete ui;
}
