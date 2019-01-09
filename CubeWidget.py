from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtOpenGL import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect

class CubeWidget(QGLWidget):

    @property
    def vector_rotate(self):
        return self._vector_rotate

    @vector_rotate.setter
    def vector_rotate(self, value):
        self._vector_rotate = value
        if not self.isHidden():
            self.updateGL()

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self._vector_rotate = [0, 0, 0]
        #self.setMinimumSize(100, 100)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -10.0)
        glRotatef(self._vector_rotate[0], 1.0, 0.0, 0.0)
        glRotatef(self._vector_rotate[1], 0.0, 1.0, 0.0)
        glRotatef(self._vector_rotate[2], 0.0, 0.0, 1.0)

        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)

        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, 1.0)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)

        glEnd()

    def setGeometry(self, *__args):
        m = min(__args[2], __args[3])
        super().setGeometry(__args[0], __args[1], m, m)


    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity()
        glFrustum(-1.0, 1.0, -1.0, 1.0, 5.0, 30.0)

        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
