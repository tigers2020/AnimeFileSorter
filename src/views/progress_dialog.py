#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
진행 상황 표시 대화 상자 구현입니다.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QObject


class Worker(QObject):
    """
    작업 스레드 클래스.
    
    별도의 스레드에서 실행할 작업을 처리합니다.
    """
    
    # 시그널 정의
    progress = Signal(int)  # 진행 상황 (0-100)
    status = Signal(str)    # 상태 메시지
    finished = Signal(object)  # 작업 완료 (결과 객체)
    error = Signal(str)     # 오류 메시지
    
    def __init__(self, task_func, *args, **kwargs):
        """
        작업자 초기화.
        
        Args:
            task_func: 실행할 작업 함수
            *args: 작업 함수에 전달할 위치 인자
            **kwargs: 작업 함수에 전달할 키워드 인자
        """
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """작업 실행."""
        try:
            # 진행 콜백 함수 생성
            def progress_callback(value, max_value=100):
                if max_value > 0:
                    percentage = min(100, int((value / max_value) * 100))
                    self.progress.emit(percentage)
            
            # 상태 콜백 함수 생성
            def status_callback(message):
                self.status.emit(message)
            
            # 콜백 함수 전달
            self.kwargs['progress_callback'] = progress_callback
            self.kwargs['status_callback'] = status_callback
            
            # 작업 실행
            result = self.task_func(*self.args, **self.kwargs)
            
            # 완료 시그널 발생
            self.finished.emit(result)
            
        except Exception as e:
            # 오류 시그널 발생
            self.error.emit(str(e))


class ProgressDialog(QDialog):
    """
    진행 상황 표시 대화 상자.
    
    시간이 오래 걸리는 작업의 진행 상황을 표시합니다.
    """
    
    def __init__(self, title, message, parent=None, cancellable=True):
        """
        진행 대화 상자 초기화.
        
        Args:
            title: 대화 상자 제목
            message: 표시할 메시지
            parent: 부모 위젯
            cancellable: 취소 가능 여부
        """
        super().__init__(parent)
        
        # 기본 설정
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)
        self.setModal(True)
        
        # 결과 저장 변수
        self.result_data = None
        self.error_message = None
        
        # 워커 스레드 변수
        self.thread = None
        self.worker = None
        
        # 레이아웃 설정
        layout = QVBoxLayout(self)
        
        # 메시지 레이블
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # 상태 레이블
        self.status_label = QLabel("준비 중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 진행 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 버튼 박스
        button_box = QDialogButtonBox()
        
        if cancellable:
            button_box.addButton(QDialogButtonBox.Cancel)
            button_box.rejected.connect(self.cancel)
        
        layout.addWidget(button_box)
    
    def run_task(self, task_func, *args, **kwargs):
        """
        작업 실행.
        
        Args:
            task_func: 실행할 작업 함수
            *args: 작업 함수에 전달할 위치 인자
            **kwargs: 작업 함수에 전달할 키워드 인자
            
        Returns:
            작업 결과 또는 None (취소 또는 오류 발생 시)
        """
        # 스레드 및 워커 생성
        self.thread = QThread()
        self.worker = Worker(task_func, *args, **kwargs)
        self.worker.moveToThread(self.thread)
        
        # 시그널 연결
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.handle_finished)
        self.worker.error.connect(self.handle_error)
        
        # 정리 연결
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.handle_thread_complete)
        
        # 스레드 시작
        self.thread.start()
        
        # 대화 상자 실행
        self.exec()
        
        # 결과 반환
        if self.error_message:
            raise RuntimeError(self.error_message)
        
        return self.result_data
    
    @Slot(int)
    def update_progress(self, value):
        """
        진행 상황 업데이트.
        
        Args:
            value: 진행률 (0-100)
        """
        self.progress_bar.setValue(value)
    
    @Slot(str)
    def update_status(self, message):
        """
        상태 메시지 업데이트.
        
        Args:
            message: 표시할 메시지
        """
        self.status_label.setText(message)
    
    @Slot(object)
    def handle_finished(self, result):
        """
        작업 완료 처리.
        
        Args:
            result: 작업 결과
        """
        self.result_data = result
    
    @Slot(str)
    def handle_error(self, error_message):
        """
        오류 처리.
        
        Args:
            error_message: 오류 메시지
        """
        self.error_message = error_message
    
    def handle_thread_complete(self):
        """스레드 완료 시 대화 상자 닫기."""
        self.accept()
    
    def cancel(self):
        """작업 취소."""
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.reject()
    
    def closeEvent(self, event):
        """대화 상자 닫기 이벤트."""
        self.cancel()
        event.accept()
    
    @staticmethod
    def run(title, message, task_func, *args, parent=None, cancellable=True, **kwargs):
        """
        진행 대화 상자 생성 및 작업 실행.
        
        Args:
            title: 대화 상자 제목
            message: 표시할 메시지
            task_func: 실행할 작업 함수
            *args: 작업 함수에 전달할 위치 인자
            parent: 부모 위젯
            cancellable: 취소 가능 여부
            **kwargs: 작업 함수에 전달할 키워드 인자
            
        Returns:
            작업 결과 또는 None
        """
        dialog = ProgressDialog(title, message, parent, cancellable)
        try:
            return dialog.run_task(task_func, *args, **kwargs)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(parent, "오류", f"작업 중 오류가 발생했습니다: {str(e)}")
            return None 