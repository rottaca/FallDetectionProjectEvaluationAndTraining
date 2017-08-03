#include "eventbuffer.h"
#include <QMutexLocker>


EventBuffer::EventBuffer():m_timeWindow(0),m_sx(0),m_sy(0)
{
}


void EventBuffer::clear()
{
    QMutexLocker locker(&m_lock);
    m_buffer.clear();
}

void EventBuffer::setup(const uint32_t timewindow, const uint16_t sx, const uint16_t sy)
{
    QMutexLocker locker(&m_lock);
    m_timeWindow = timewindow;
    m_sx = sx;
    m_sy = sy;
    m_buffer.clear();
}

void EventBuffer::addEvent(const sDVSEventDepacked &event)
{
    QMutexLocker locker(&m_lock);
    // Remove all old events
    while (m_buffer.size() > 0 &&
            abs(event.ts - m_buffer.back().ts) > m_timeWindow) {
        m_buffer.pop_back();
    }

    // Add new event
    m_buffer.push_front(event);
}
void EventBuffer::addEvents(std::queue<sDVSEventDepacked> & events)
{
    if(events.size() == 0)
        return;

    int32_t newTsStart = events.back().ts;
    QMutexLocker locker(&m_lock);

    // Remove all old events
    // Here, we have to lock for the whole period

    while (m_buffer.size() > 0 &&
            abs(newTsStart - m_buffer.back().ts) > m_timeWindow) {
        m_buffer.pop_back();
    }


    // Add events
    while(!events.empty()) {
        const sDVSEventDepacked &ev = events.front();
        // Don't block for the whole function or other threads are slowed down

        if(m_buffer.size() > 0 && m_buffer.front().ts > events.front().ts)
            printf("Time jump: %d to %d\n", m_buffer.front().ts,events.front().ts);

        {
            m_buffer.push_front(ev);
        }

        events.pop();
    }

    //printf("Buff: %zu\n",m_buffer.size());
}

QImage EventBuffer::toImage()
{
    QImage img(m_sx,m_sy,QImage::Format_RGB888);

    img.fill(Qt::white);
    QMutexLocker locker(&m_lock);
    // Get current time and color according to temporal distance
    uint32_t currTime = m_buffer.front().ts;

    for(sDVSEventDepacked e:m_buffer) {
        uchar c = 255*(currTime-e.ts)/m_timeWindow;
        *(img.scanLine(e.y) + 3*e.x) = c;
        *(img.scanLine(e.y) + 3*e.x + 1) = c;
        *(img.scanLine(e.y) + 3*e.x + 2) = c;
    }
    return img;
}
