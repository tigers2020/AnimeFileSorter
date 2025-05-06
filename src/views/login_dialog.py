#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AniDB 로그인 대화 상자 구현입니다.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFormLayout, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSettings


class LoginDialog(QDialog):
    """
    AniDB 로그인 대화 상자.
    
    사용자 이름과 비밀번호를 입력받고 로그인을 시도합니다.
    """
    
    # 로그인 성공 시그널 (사용자 이름, 비밀번호)
    login_success = Signal(str, str)
    
    def __init__(self, parent=None):
        """로그인 대화 상자 초기화."""
        super().__init__(parent)
        
        # 기본 설정
        self.setWindowTitle("AniDB 로그인")
        self.setMinimumWidth(350)
        self.setModal(True)
        
        # 레이아웃 설정
        layout = QVBoxLayout(self)
        
        # 설명 레이블
        info_label = QLabel(
            "AniDB API를 사용하기 위해 로그인이 필요합니다.\n"
            "등록된 AniDB 계정으로 로그인하세요."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 폼 레이아웃
        form_layout = QFormLayout()
        
        # 사용자 이름 입력
        self.username_input = QLineEdit()
        form_layout.addRow("사용자 이름:", self.username_input)
        
        # 비밀번호 입력
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("비밀번호:", self.password_input)
        
        # 사용자 이름 저장 체크박스
        self.save_username_check = QCheckBox("사용자 이름 저장")
        self.save_username_check.setChecked(True)
        form_layout.addRow("", self.save_username_check)
        
        layout.addLayout(form_layout)
        
        # 버튼 박스
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._handle_login)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 저장된 사용자 이름 로드
        self._load_username()
    
    def _load_username(self):
        """저장된 사용자 이름 로드."""
        settings = QSettings("AnimeFileSorter", "AniDB")
        username = settings.value("username", "")
        save_username = settings.value("save_username", True, type=bool)
        
        self.username_input.setText(username)
        self.save_username_check.setChecked(save_username)
        
        # 사용자 이름이 있으면 비밀번호 필드에 포커스
        if username:
            self.password_input.setFocus()
    
    def _save_username(self, username):
        """사용자 이름 저장."""
        settings = QSettings("AnimeFileSorter", "AniDB")
        
        if self.save_username_check.isChecked():
            settings.setValue("username", username)
        else:
            settings.setValue("username", "")
        
        settings.setValue("save_username", self.save_username_check.isChecked())
    
    def _handle_login(self):
        """로그인 버튼 클릭 핸들러."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # 입력 검증
        if not username:
            QMessageBox.warning(self, "입력 오류", "사용자 이름을 입력하세요.")
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "입력 오류", "비밀번호를 입력하세요.")
            self.password_input.setFocus()
            return
        
        # 사용자 이름 저장
        self._save_username(username)
        
        # 성공 시그널 발생 및 대화 상자 닫기
        self.login_success.emit(username, password)
        self.accept()
    
    @staticmethod
    def get_credentials(parent=None):
        """
        로그인 대화 상자를 표시하고 사용자 이름과 비밀번호를 반환.
        
        Args:
            parent: 부모 위젯
            
        Returns:
            (사용자 이름, 비밀번호) 튜플 또는 취소 시 (None, None)
        """
        dialog = LoginDialog(parent)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            return dialog.username_input.text().strip(), dialog.password_input.text()
        else:
            return None, None 