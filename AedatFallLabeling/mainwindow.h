#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include <fstream>

#include <queue>

#include "camerahandler.h"
#include "eventbuffer.h"

namespace Ui
{
class MainWindow;
}

class MainWindow : public QMainWindow,
    public CameraHandler::IDVSEventReciever,
    public CameraHandler::IFrameReciever
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

    void callbackProcessingStopped()
    {
        processingStopped = true;
    }

    void newEvent(const sDVSEventDepacked & event);
    void newFrame(const caerFrameEvent &frame);
public slots:
    void redrawUI();
    void keyPressEvent(QKeyEvent *e);

    void onClickRestart();
    void onClickCancel();
    void onClickFinish();

private:
    Ui::MainWindow *ui;
    CameraHandler camHandler;
    bool processingStopped;
    QTimer* timer;

    int m_sx,m_sy;

    QMutex m_queueMutex;
    std::queue<sDVSEventDepacked> m_eventQueue;
    EventBuffer m_eventBuffer;

    QMutex m_frameMutex;
    QImage m_currFrame;

    float playSpeed;

    enum tFallState {NONE,FALLING,FALLING_DONE,GETTIN_UP} fallState;
    std::fstream fallLabelFile;
    QString labelFileName;

    int timeWindowSize;
    float maxSpeed,minSpeed,incSpeed;
};

#endif // MAINWINDOW_H
