"""Elsewhere Studio — dedicated photographic development desktop application.

No brushes, painted gradients, synthetic photographic textures, or generation.
Requires dependencies at build time; Windows distribution bundles the runtime.
"""
from __future__ import annotations
import copy
import json
import sys
from pathlib import Path
import numpy as np
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QSize, QPointF
from PySide6.QtGui import QAction, QColor, QFont, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
    QSplitter, QScrollArea, QTabWidget, QTabBar, QLabel, QPushButton, QToolButton, QComboBox,
    QSlider, QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QProgressBar,
    QLineEdit, QCheckBox, QGroupBox, QSizePolicy
)

import engine
from engine import DEFAULTS, DEFAULT_GEOMETRY, GROUPS, WORKSPACE_TABS
from album_catalog import COVERS, ALBUM_CONTROLS, FEATURE_DESCRIPTIONS
from era_catalog import ERAS
from control_descriptions import DESCRIPTIONS
from io_formats import open_image, save_image
from recipe import validated_recipe

APP_NAME='ELSEWHERE STUDIO'
APP_VERSION='0.8.0 · Caretaker / Eras'

STYLE = '''
QWidget{background:#17191e;color:#d9dee8;font:10pt "Segoe UI"}
QMainWindow{background:#111318}
QMenuBar,QMenu{background:#22252e;border:0;color:#d9dee8}
QMenuBar::item{padding:7px 11px} QMenuBar::item:selected,QMenu::item:selected{background:#404a61}
QFrame#top{background:#20232b;border-bottom:1px solid #343b48}
QFrame#rail{background:#191c22;border-right:1px solid #2e3340}
QFrame#inspector{background:#20232a;border-left:1px solid #343b48}
QFrame#stats{background:#20232a;border:1px solid #343a48;border-radius:6px}
QLabel#kicker{color:#94a9d7;font-size:9pt;font-weight:700;letter-spacing:2px}
QLabel#secondary{color:#98a1b0}
QLabel#brand{color:#eef1f8;font-size:18pt;font-weight:800;letter-spacing:2px}
QPushButton{background:#2a2f3a;color:#e5eaf2;border:1px solid #424958;border-radius:5px;padding:9px 12px}
QPushButton:hover{background:#353f52;border-color:#6a7ea9}
QPushButton:disabled{color:#737986;border-color:#343a44}
QPushButton#primary{background:#617eae;color:#ffffff;border:1px solid #8299c0;font-weight:700}
QPushButton#primary:hover{background:#7590ba}
QPushButton#nav{background:transparent;border:0;border-left:3px solid transparent;border-radius:0;text-align:left;padding:12px 14px;font-weight:600;color:#99a5b9}
QPushButton#nav:hover{background:#282e3a}
QPushButton#nav:checked{background:#30394a;border-left:3px solid #a6b9ec;color:#fff}
QSlider::groove:horizontal{height:4px;background:#414956;border-radius:2px}
QSlider::handle:horizontal{background:#aec1ef;width:12px;margin:-5px 0;border-radius:6px}
QSlider::sub-page:horizontal{background:#7c96c8;border-radius:2px}
QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox{background:#15181f;color:#e1e6f0;border:1px solid #454d5c;border-radius:4px;padding:6px}
QComboBox QAbstractItemView{background:#222631;selection-background-color:#4b5b78}
QScrollArea{border:0;background:transparent} QScrollArea>QWidget>QWidget{background:transparent}
QGroupBox{border:1px solid #3b4251;border-radius:5px;margin-top:14px;padding:8px 5px 6px;font-weight:700;color:#adbee8}
QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 6px}
QListWidget{background:#191d25;border:1px solid #363e4e;border-radius:4px;outline:0}
QListWidget::item{padding:9px} QListWidget::item:selected{background:#3d506f;color:white}
QStatusBar{background:#20232b;color:#b3bdcf;border-top:1px solid #363b49}
QProgressBar{background:#272e3b;border:0;border-radius:3px;height:5px}
QProgressBar::chunk{background:#8ba5dd;border-radius:3px}
QTabWidget::pane{border:0;background:#20232a}
QTabBar::tab{background:#252a34;padding:9px 14px;color:#94a0b4}
QTabBar::tab:selected{background:#3a475f;color:#f6f8ff}
'''

class ImageCanvas(QGraphicsView):
    dropped = Signal(str)
    def __init__(self):
        super().__init__()
        self.scene=QGraphicsScene(self);self.setScene(self.scene)
        self.item=QGraphicsPixmapItem();self.scene.addItem(self.item)
        self.setBackgroundBrush(QColor('#0d0f14'))
        self.setFrameShape(QFrame.NoFrame)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setAcceptDrops(True)
        self.has_photo=False
    def set_picture(self, image):
        pix=QPixmap.fromImage(image)
        was_empty=not self.has_photo
        self.item.setPixmap(pix);self.scene.setSceneRect(self.item.boundingRect())
        self.has_photo=True
        if was_empty: self.fit_image()
    def fit_image(self):
        if self.has_photo:self.fitInView(self.item,Qt.KeepAspectRatio)
    def clear_picture(self):
        self.item.setPixmap(QPixmap())
        self.has_photo=False
        self.resetTransform()
        self.scene.setSceneRect(0,0,1,1)
    def wheelEvent(self,event):
        if not self.has_photo:return
        factor=1.15 if event.angleDelta().y()>0 else (1/1.15)
        self.scale(factor,factor)
    def resizeEvent(self,event):
        super().resizeEvent(event)
        if self.has_photo and self.transform().m11()<.15:self.fit_image()
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls():e.acceptProposedAction()
        else:super().dragEnterEvent(e)
    def dragMoveEvent(self,e):
        if e.mimeData().hasUrls():e.acceptProposedAction()
        else:super().dragMoveEvent(e)
    def dropEvent(self,e):
        if e.mimeData().hasUrls():
            for u in e.mimeData().urls():
                if u.isLocalFile():self.dropped.emit(u.toLocalFile());e.acceptProposedAction();return
        super().dropEvent(e)

class Histogram(QWidget):
    def __init__(self):
        super().__init__();self.setMinimumHeight(114);self.hists=None
    def set_image(self,arr):
        # Histogram is based on the actual rendered preview, not the ungraded RAW.
        if arr is None: return
        a=arr[::max(1,arr.shape[0]//350),::max(1,arr.shape[1]//350),:]
        self.hists=[np.histogram(a[...,i],bins=128,range=(0,256))[0].astype(float) for i in range(3)]
        self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(),QColor('#14171d'))
        p.setPen(QPen(QColor('#333a48'),1))
        for i in range(1,4):
            y=self.height()*i/4;p.drawLine(0,int(y),self.width(),int(y))
        if not self.hists:return
        mx=max(np.percentile(h,98) for h in self.hists)+1e-5
        for hist,color in zip(self.hists,[QColor(230,95,96,130),QColor(85,220,156,120),QColor(111,156,252,140)]):
            path=QPainterPath();path.moveTo(0,self.height())
            for i,v in enumerate(hist):
                x=i/(len(hist)-1)*self.width();y=self.height()-min(v/mx,1)*self.height()
                path.lineTo(x,y)
            path.lineTo(self.width(),self.height());path.closeSubpath()
            p.fillPath(path,color)

class IOJob(QThread):
    loaded=Signal(object,dict,bool,str,int)
    exported=Signal(str,int)
    error=Signal(str,str,int)
    def __init__(self,mode,path,settings=None,geometry=None,options=None,token=0,album_id='none',era_id='none',level_id='l0'):
        super().__init__();self.mode=mode;self.path=path
        self.token=token
        self.settings=dict(settings or {});self.geometry=dict(geometry or {})
        self.options=dict(options or {})
        self.album_id=album_id;self.era_id=era_id;self.level_id=level_id
    def run(self):
        try:
            if self.mode=='open':
                arr,meta,linear=open_image(self.path,preview=True,options=self.options)
                self.loaded.emit(arr,meta,linear,self.path,self.token)
            elif self.mode=='export':
                if Path(self.options['source']).resolve()==Path(self.path).resolve():
                    raise ValueError('Export destination must differ from the source photograph')
                src,meta,linear=open_image(self.options['source'],preview=False,options=self.options)
                bits=8 if Path(self.path).suffix.lower() in ('.jpg','.jpeg') else 16
                out=engine.render(src,self.settings,self.geometry,source_linear=linear,out_bits=bits,album_id=self.album_id,era_id=self.era_id,level_id=self.level_id)
                save_image(self.path,out)
                self.exported.emit(self.path,bits)
        except Exception as ex:
            self.error.emit(f'{type(ex).__name__}: {ex}',self.path,self.token)

class RenderJob(QThread):
    ready=Signal(object,int)
    error=Signal(str,int)
    def __init__(self,rgb,settings,geometry,linear,version,album_id='none',era_id='none',level_id='l0'):
        super().__init__();self.rgb=rgb;self.settings=dict(settings)
        self.geometry=dict(geometry);self.linear=linear;self.version=version
        self.album_id=album_id;self.era_id=era_id;self.level_id=level_id
    def run(self):
        try:
            result=engine.render(self.rgb,self.settings,self.geometry,
                source_linear=self.linear,out_bits=8,fast=False,album_id=self.album_id,era_id=self.era_id,level_id=self.level_id)
            self.ready.emit(result,self.version)
        except Exception as e:self.error.emit(str(e),self.version)

class Elsewhere(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{APP_NAME} — {APP_VERSION}')
        self.resize(1560,970);self.setMinimumSize(1080,700)
        self.setStyleSheet(STYLE)
        self.image_data=None;self.linear=False;self.filepath=None;self.meta={}
        self.settings=DEFAULTS.copy();self.geometry=DEFAULT_GEOMETRY.copy()
        self.album_id=next(iter(COVERS));self.era_id='1970s';self.level_id='l0' 
        self.raw_options={'white_balance':'camera','highlight_mode':'blend'}
        self.slider_controls={};self.curve_controls={};self.wheel_controls={}
        self.raw_controls=[];self.current_preview=None
        self.version=0;self.load_token=0;self.render_thread=None;self.active_jobs=[]
        self._close_pending=False
        self.undo_states=[];self.redo_states=[];self.rebuilding=False
        self.original_visible=False;self.cached_original=None
        self.timer=QTimer(self);self.timer.setSingleShot(True)
        self.timer.setInterval(210);self.timer.timeout.connect(self.render_debounced)
        self.init_ui();self.init_menu();self.sync_ui()
        for c in self.raw_controls:c.setEnabled(False)
        self.statusBar().showMessage('Ready  ·  Open your photograph to begin')
    def snapshot(self):
        return (copy.deepcopy(self.settings),copy.deepcopy(self.geometry),self.album_id,self.era_id,self.level_id)
    def record_undo(self):
        snap=self.snapshot()
        if not self.undo_states or self.undo_states[-1]!=snap:
            self.undo_states.append(snap)
            self.undo_states=self.undo_states[-70:]
        # Any new editing action invalidates the redo branch, including when
        # its starting state is identical to the last stored undo snapshot.
        self.redo_states.clear()
    def undo(self):
        if not self.undo_states:return
        self.redo_states.append(self.snapshot())
        self.settings,self.geometry,self.album_id,self.era_id,self.level_id=self.undo_states.pop()
        self.sync_selections();self.sync_ui();self.schedule()
    def redo(self):
        if not self.redo_states:return
        self.undo_states.append(self.snapshot())
        self.settings,self.geometry,self.album_id,self.era_id,self.level_id=self.redo_states.pop()
        self.sync_selections();self.sync_ui();self.schedule()
    def init_menu(self):
        menu=self.menuBar()
        files=menu.addMenu('File')
        for label,shortcut,fn in [('Open photograph…','Ctrl+O',self.open_dialog),
                                  ('Export photograph…','Ctrl+Shift+S',self.export_dialog),
                                  ('Save development recipe…','Ctrl+S',self.save_recipe),
                                  ('Load development recipe…','Ctrl+L',self.load_recipe)]:
            a=QAction(label,self);a.setShortcut(shortcut);a.triggered.connect(fn);files.addAction(a)
        edit=menu.addMenu('Edit')
        for label,shortcut,fn in [('Undo','Ctrl+Z',self.undo),('Redo','Ctrl+Y',self.redo),
                                  ('Reset grade','Ctrl+R',self.reset_grade)]:
            a=QAction(label,self);a.setShortcut(shortcut);a.triggered.connect(fn);edit.addAction(a)
        view=menu.addMenu('View')
        for label,shortcut,fn in [('Fit image','Ctrl+0',self.canvas.fit_image),
                                  ('Before / after','\\',self.toggle_original)]:
            a=QAction(label,self);a.setShortcut(shortcut);a.triggered.connect(fn);view.addAction(a)
    def init_ui(self):
        outer=QWidget();self.setCentralWidget(outer)
        layout=QVBoxLayout(outer);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
        top=QFrame();top.setObjectName('top');topbox=QVBoxLayout(top);topbox.setContentsMargins(18,12,18,10);topbox.setSpacing(10)
        top_row=QHBoxLayout()
        brand=QVBoxLayout();head=QLabel('ELSEWHERE');head.setObjectName('brand');brand.addWidget(head)
        sub=QLabel('LIMINAL PHOTOGRAPHIC LABORATORY');sub.setObjectName('kicker');brand.addWidget(sub)
        top_row.addLayout(brand);top_row.addStretch()
        self.before_btn=QPushButton('Before / After');self.before_btn.setCheckable(True)
        self.before_btn.clicked.connect(self.toggle_original);top_row.addWidget(self.before_btn)
        fit=QPushButton('Fit to Window');fit.clicked.connect(self.canvas_fit_action);top_row.addWidget(fit)
        open_btn=QPushButton('Open Photo');open_btn.clicked.connect(self.open_dialog);top_row.addWidget(open_btn)
        self.export_btn=QPushButton('Export');self.export_btn.setObjectName('primary')
        self.export_btn.clicked.connect(self.export_dialog);self.export_btn.setEnabled(False)
        top_row.addWidget(self.export_btn)
        topbox.addLayout(top_row)
        self.workspace_bar=QTabBar();self.workspace_bar.setDocumentMode(True);self.workspace_bar.setExpanding(False)
        self.workspace_bar.setStyleSheet('QTabBar::tab{min-width:125px;padding:12px 10px;}')
        for name in ['Core','Backrooms','Album Covers','Institutional','Temporal','Geometry','RAW Settings']:
            self.workspace_bar.addTab(name)
        self.workspace_bar.currentChanged.connect(self.change_workspace)
        topbox.addWidget(self.workspace_bar)
        layout.addWidget(top)
        split=QSplitter(Qt.Horizontal);split.setChildrenCollapsible(False);layout.addWidget(split,1)
        center=QWidget();center_l=QVBoxLayout(center);center_l.setContentsMargins(6,6,6,4)
        self.canvas=ImageCanvas();self.canvas.dropped.connect(self.open_path)
        center_l.addWidget(self.canvas,1)
        status=QHBoxLayout()
        self.filename=QLabel('No photograph open');self.filename.setObjectName('secondary')
        status.addWidget(self.filename);status.addStretch()
        self.bitbadge=QLabel('RAW · JPEG · PNG · TIFF');self.bitbadge.setObjectName('secondary')
        status.addWidget(self.bitbadge);center_l.addLayout(status)
        split.addWidget(center)
        right=QFrame();right.setObjectName('inspector');right.setMinimumWidth(360);right.setMaximumWidth(520)
        right_l=QVBoxLayout(right);right_l.setContentsMargins(10,10,10,10);right_l.setSpacing(8)
        stats=QFrame();stats.setObjectName('stats');stats_l=QVBoxLayout(stats);stats_l.setContentsMargins(12,10,12,10)
        kicker=QLabel('LIVE RGB HISTOGRAM');kicker.setObjectName('kicker');stats_l.addWidget(kicker)
        self.hist=Histogram();stats_l.addWidget(self.hist)
        self.metadata=QLabel('No photograph loaded');self.metadata.setWordWrap(True)
        self.metadata.setObjectName('secondary');stats_l.addWidget(self.metadata)
        right_l.addWidget(stats)
        self.panel_title=QLabel('CORE');self.panel_title.setObjectName('kicker');right_l.addWidget(self.panel_title)
        self.pages_stack=QTabWidget();self.pages_stack.tabBar().hide()
        self.workspace_pages={}
        for name in ['Core','Backrooms','Album Covers','Institutional','Temporal','Geometry','RAW Settings']:
            if name in WORKSPACE_TABS:
                page=self.make_workspace_page(name)
            elif name=='Geometry':
                page=self.make_geometry()
            elif name=='RAW Settings':
                page=self.make_raw_options()
            self.workspace_pages[name]=page
            self.pages_stack.addTab(page,name)
        right_l.addWidget(self.pages_stack,1)
        self.progress=QProgressBar();self.progress.setMaximumHeight(6);self.progress.hide()
        right_l.addWidget(self.progress)
        split.addWidget(right);split.setSizes([1040,420]);self.change_workspace(0)
    def change_workspace(self,index):
        name=self.workspace_bar.tabText(index)
        self.panel_title.setText(name.upper())
        for i in range(self.pages_stack.count()):
            if self.pages_stack.tabText(i)==name:
                self.pages_stack.setCurrentIndex(i);break
    def make_workspace_page(self,name):
        if name=='Backrooms':return self.make_backrooms_workspace()
        if name=='Album Covers':return self.make_album_workspace()
        if name=='Temporal':return self.make_era_workspace()
        w,box=self.page()
        descriptions={
            'Core':'Shared photographic development for CR3, JPG, PNG and TIFF. The specialized workspaces above are the identity of Elsewhere.',
            'Institutional':'Source-aware adjustments for office, corridor, school, hospital and other fluorescent architecture. Fifteen controls, all editable.'
        }
        note=QLabel(descriptions.get(name,''));note.setWordWrap(True);note.setObjectName('secondary')
        box.addWidget(note)
        for section in WORKSPACE_TABS.get(name,[]):
            group=QGroupBox(section);v=QVBoxLayout(group)
            for item in GROUPS[section]:v.addWidget(self.control(*item))
            if section=='Curves':
                reset=QPushButton('Reset curve to linear');reset.clicked.connect(self.reset_curve);v.addWidget(reset)
            box.addWidget(group)
        box.addStretch();return w
    def make_backrooms_workspace(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0)
        expl=QLabel('FOUR DISTINCT ARCHITECTURAL PHOTOGRAPHIC LABS · 10 controls per level. Select a level to activate that level’s controls. No one-click grades.')
        expl.setWordWrap(True);expl.setObjectName('secondary');v.addWidget(expl)
        tabs=QTabWidget();self.level_tabs=tabs
        levels=[('l0','LEVEL 0 · YELLOW HALLS','Backrooms Level 0 · Fluorescent yellow walls, institutional monotony, old carpet and nonuniform light.'),
                ('l1','LEVEL 1 · PARKING GARAGE','Backrooms Level 1 · Concrete, dim industrial lighting, cool shadows and sporadic warmth.'),
                ('l4','LEVEL 4 · OFFICES','Backrooms Level 4 · Office interiors, dead fluorescent atmosphere, muted beige and unnatural stillness.'),
                ('l5','LEVEL 5 · HOTEL','Backrooms Level 5 · Old hotel corridors and ballrooms, amber lights, heavy fabrics and receding depth.')]
        for code,label,description in levels:
            pg,box=self.page()
            desc=QLabel(description);desc.setWordWrap(True);desc.setObjectName('secondary');box.addWidget(desc)
            for item in GROUPS['Backrooms · Level '+code[1:]]:
                box.addWidget(self.control(*item))
            box.addStretch();tabs.addTab(pg,label)
        tabs.currentChanged.connect(self.level_changed)
        v.addWidget(tabs,1);return w
    def level_changed(self,index):
        ids=['l0','l1','l4','l5'];new=ids[index]
        if self.level_id==new:return
        self.record_undo();self.level_id=new;self.schedule()
    def make_album_workspace(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0);v.setSpacing(8)
        note=QLabel('THE CARETAKER · DISCOGRAPHY REFERENCE. Select a named release, then shape your own photograph with its 5 artwork-specific and 15 shared controls. Selecting alone never grades the image.')
        note.setWordWrap(True);note.setObjectName('secondary');v.addWidget(note)
        selector=QComboBox();self.album_combo=selector
        for cover_id,data in COVERS.items():selector.addItem(f"{data['title']}  ·  {data['year']}",cover_id)
        selector.currentIndexChanged.connect(self.album_changed);v.addWidget(selector)
        self.album_title=QLabel();self.album_title.setWordWrap(True);self.album_title.setStyleSheet('font-weight:700;color:#dce5ff;font-size:11pt');v.addWidget(self.album_title)
        self.album_description=QLabel();self.album_description.setObjectName('secondary');self.album_description.setWordWrap(True);v.addWidget(self.album_description)
        self.album_scroller=QScrollArea();self.album_scroller.setWidgetResizable(True)
        self.album_scroll_content=QWidget();self.album_controls_box=QVBoxLayout(self.album_scroll_content)
        self.album_controls_box.setContentsMargins(4,6,4,6);self.album_controls_box.setSpacing(10)
        self.album_scroller.setWidget(self.album_scroll_content);v.addWidget(self.album_scroller,1)
        self.refresh_album_controls();return w
    def album_changed(self,index):
        new=self.album_combo.itemData(index)
        if not new or new==self.album_id:return
        self.record_undo();self.album_id=new;self.refresh_album_controls();self.schedule()
    def refresh_album_controls(self):
        meta=COVERS[self.album_id]
        self.album_title.setText(f"{meta['title']}  ({meta['year']})\nCover: {meta['artwork']}")
        self.album_description.setText(meta['description']+'\nNote: Elsewhere changes your photograph; it does not create or paste the cover artwork.')
        # Remove old dynamic widgets and stale controls before rebuilding.
        for key in list(self.slider_controls):
            if key.startswith('cover_'):del self.slider_controls[key]
        box=self.album_controls_box
        while box.count():
            item=box.takeAt(0)
            if item.widget():item.widget().deleteLater()
        g=QGroupBox('FIVE CONTROLS · '+meta['artwork']);f=QVBoxLayout(g)
        for i,label in enumerate(meta['features']):
            k=f'cover_{self.album_id}_{i}'
            f.addWidget(self.control(k,label,0,100,1))
        box.addWidget(g)
        shared=QGroupBox('15 PRINT / PAINT / MEMORY CONTROLS');sv=QVBoxLayout(shared)
        for key,label,description in ALBUM_CONTROLS:
            sv.addWidget(self.control(key,label,0,100,1))
        box.addWidget(shared);box.addStretch()
        self.sync_ui()
    def make_era_workspace(self):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(0,0,0,0)
        explanation=QLabel('TEMPORAL ERAS · Exactly 1970s, 1980s, 1990s, 2000s and 2010s. Choose one era, then adjust its own 15 photo-processing controls. No presets.')
        explanation.setWordWrap(True);explanation.setObjectName('secondary');v.addWidget(explanation)
        tabs=QTabWidget();self.era_tabs=tabs
        for decade,data in ERAS.items():
            pg,box=self.page()
            note=QLabel(data['summary']);note.setWordWrap(True);note.setObjectName('secondary');box.addWidget(note)
            for key,label,description in data['controls']:
                box.addWidget(self.control(key,label,0,100,1))
            box.addStretch();tabs.addTab(pg,decade)
        tabs.currentChanged.connect(self.era_changed)
        v.addWidget(tabs,1);return w
    def era_changed(self,index):
        new=list(ERAS)[index]
        if self.era_id==new:return
        self.record_undo();self.era_id=new;self.schedule()
    def page(self):
        w=QWidget();outer=QVBoxLayout(w);outer.setContentsMargins(0,0,0,0)
        sc=QScrollArea();sc.setWidgetResizable(True)
        content=QWidget();box=QVBoxLayout(content);box.setContentsMargins(4,5,4,5);box.setSpacing(13)
        sc.setWidget(content);outer.addWidget(sc)
        return w,box
    def control(self, key, label, low, high, step=1, *, geom=False):
        w=QWidget();v=QVBoxLayout(w);v.setContentsMargins(1,2,1,2);v.setSpacing(5)
        top=QHBoxLayout();nam=QLabel(label);top.addWidget(nam);top.addStretch()
        number=QLabel('0');number.setMinimumWidth(52);number.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        number.setStyleSheet('color:#bdcbef;font-weight:600')
        top.addWidget(number);v.addLayout(top)
        slider=QSlider(Qt.Horizontal)
        d=20 if step==.05 else 1
        slider.setRange(round(low*d),round(high*d));slider.setSingleStep(max(1,round(step*d)))
        def changed(n):
            if self.rebuilding:return
            target=self.geometry if geom else self.settings
            # The value can also change with keyboard arrows or the mouse wheel.
            # Snapshot these before changes; mouse drags snapshot on sliderPressed.
            if not slider.isSliderDown():self.record_undo()
            target[key]=n/d;number.setText(f'{n/d:.2f}' if d==20 else f'{n/d:.0f}')
            self.schedule()
        slider.valueChanged.connect(changed)
        slider.sliderPressed.connect(self.record_undo)
        v.addWidget(slider)
        description=DESCRIPTIONS.get(key)
        if not description and key.startswith('cover_'):
            try: description=FEATURE_DESCRIPTIONS[int(key.rsplit('_',1)[1])]
            except (ValueError,IndexError): description=None
        if not description:
            for info in ERAS.values():
                for k,lab,detail in info['controls']:
                    if key==k:description=detail;break
                if description:break
        if not description:
            for k,lab,detail in ALBUM_CONTROLS:
                if key==k:description=detail;break
        if description:
            explain=QLabel(description);explain.setWordWrap(True)
            explain.setStyleSheet('color:#8f9cb1;font-size:9pt;padding-bottom:8px;')
            slider.setToolTip(description);v.addWidget(explain)
        self.slider_controls[('geom_' if geom else '')+key]=(slider,number,d)
        return w
    def make_group(self,section):
        w,box=self.page()
        for item in GROUPS[section]:box.addWidget(self.control(*item))
        box.addStretch();return w
    def make_geometry(self):
        w,box=self.page()
        text=QLabel('Move, zoom, or rotate your entire photograph. No perspective corrections or painted adjustments.')
        text.setWordWrap(True);text.setObjectName('secondary');box.addWidget(text)
        for args in [('move_x','Horizontal position (%)',-50,50),
                     ('move_y','Vertical position (%)',-50,50),
                     ('zoom','Zoom (%)',50,200),('rotation','Rotation (°)',-180,180)]:
            box.addWidget(self.control(*args,geom=True))
        b=QPushButton('Reset geometry');b.clicked.connect(self.reset_geometry);box.addWidget(b)
        box.addStretch();return w
    def make_raw_options(self):
        w,box=self.page()
        note=QLabel('Sensor-stage options appear only for RAW photographs. JPG/PNG can use all other development, color, optical and liminal controls.')
        note.setWordWrap(True);note.setObjectName('secondary');box.addWidget(note)
        title=QLabel('Demosaicing white balance');box.addWidget(title)
        self.wb_combo=QComboBox();self.wb_combo.addItems(['Camera','Auto','Daylight']);box.addWidget(self.wb_combo)
        title2=QLabel('Sensor highlight decoding');box.addWidget(title2)
        self.highlight_combo=QComboBox();self.highlight_combo.addItems(['Blend','Clip','Reconstruct'])
        box.addWidget(self.highlight_combo)
        btn=QPushButton('Re-develop RAW preview');btn.clicked.connect(self.redecode_raw);box.addWidget(btn)
        self.raw_controls=[self.wb_combo,self.highlight_combo,btn]
        box.addStretch();return w
    def reset_curve(self):
        self.record_undo()
        for n in (0,25,50,75,100):self.settings[f'curve_{n}']=float(n)
        self.sync_ui();self.schedule()
    def reset_geometry(self):
        self.record_undo();self.geometry=DEFAULT_GEOMETRY.copy();self.sync_ui();self.schedule()
    def reset_grade(self):
        self.record_undo();self.settings=DEFAULTS.copy();self.sync_ui();self.schedule()
    def sync_selections(self):
        if hasattr(self,'album_combo'):
            idx=self.album_combo.findData(self.album_id)
            if idx>=0:
                self.album_combo.blockSignals(True);self.album_combo.setCurrentIndex(idx);self.album_combo.blockSignals(False)
                self.refresh_album_controls()
        if hasattr(self,'level_tabs'):
            idx=['l0','l1','l4','l5'].index(self.level_id)
            self.level_tabs.blockSignals(True);self.level_tabs.setCurrentIndex(idx);self.level_tabs.blockSignals(False)
        if hasattr(self,'era_tabs'):
            idx=list(ERAS).index(self.era_id)
            self.era_tabs.blockSignals(True);self.era_tabs.setCurrentIndex(idx);self.era_tabs.blockSignals(False)
    def sync_ui(self):
        self.rebuilding=True
        try:
            for key,(slider,label,d) in self.slider_controls.items():
                val=self.geometry.get(key[5:]) if key.startswith('geom_') else self.settings.get(key)
                if val is None:continue
                slider.setValue(int(round(val*d)))
                label.setText(f'{val:.2f}' if d==20 else f'{val:.0f}')
        finally:self.rebuilding=False
    def open_dialog(self):
        path,_=QFileDialog.getOpenFileName(self,'Open your photograph','',
            'Photographs (*.cr3 *.CR3 *.cr2 *.CR2 *.dng *.DNG *.nef *.NEF *.arw *.ARW *.raf *.RAF *.orf *.ORF *.rw2 *.RW2 *.pef *.PEF *.srw *.SRW *.jpg *.jpeg *.JPG *.png *.PNG *.tif *.tiff *.TIF *.bmp);;All files (*)')
        if path:self.open_path(path)
    def start_job(self,job):
        self.active_jobs.append(job)
        job.finished.connect(lambda j=job:self.finish_job(j))
        job.start()
    def finish_job(self,job):
        if job in self.active_jobs:self.active_jobs.remove(job)
        if not self.active_jobs:self.progress.hide()
        if self._close_pending:self._finish_pending_close()
    def busy(self,text):
        self.progress.setRange(0,0);self.progress.show();self.statusBar().showMessage(text)
    def open_path(self,path,*,preserve_edits=False):
        if not Path(path).is_file():return
        self.load_token+=1
        self.version+=1  # Invalidate previews from the previously opened image.
        self.timer.stop()
        self.filepath=path;self.image_data=None;self.current_preview=None;self.cached_original=None
        self.canvas.clear_picture();self.hist.hists=None;self.hist.update()
        self.export_btn.setEnabled(False)
        for control in self.raw_controls:control.setEnabled(False)
        self.original_visible=False;self.before_btn.setChecked(False)
        self.before_btn.setText('Before / After')
        if not preserve_edits:
            self.settings=DEFAULTS.copy();self.geometry=DEFAULT_GEOMETRY.copy()
            self.sync_ui();self.undo_states.clear();self.redo_states.clear()
        self.filename.setText(Path(path).name);self.busy('Decoding photograph…')
        job=IOJob('open',path,options=self.raw_options,token=self.load_token)
        job.loaded.connect(self.loaded)
        job.error.connect(self.failed)
        self.start_job(job)
    def loaded(self,arr,meta,linear,path,token):
        if token!=self.load_token or path!=self.filepath:return
        self.image_data=arr;self.linear=linear;self.meta=meta
        self.filename.setText(Path(path).name+'  ·  '+meta.get('resolution',''))
        self.bitbadge.setText(meta.get('bit_depth','')+'  ·  '+meta.get('format',''))
        notes=[meta[k] for k in ('input_profile','alpha') if meta.get(k)]
        self.metadata.setText(f"{meta.get('camera','')}   ·   ISO {meta.get('iso','—')}\n{meta.get('resolution','')}" + ''.join(f"\n{note}" for note in notes))
        self.export_btn.setEnabled(True)
        for control in self.raw_controls:control.setEnabled(linear)
        self.cached_original=engine.render(arr,DEFAULTS,DEFAULT_GEOMETRY,
                                           source_linear=linear,out_bits=8,fast=True)
        self.schedule();self.statusBar().showMessage('Loaded · All editing panels available')
    def failed(self,msg,path,token):
        # Ignore errors from superseded openings; retain errors from exports.
        if token and token!=self.load_token:return
        is_export=token==0
        QMessageBox.critical(self,'Export failed' if is_export else 'Photograph could not be opened',msg)
        if not is_export:self.export_btn.setEnabled(False)
        self.statusBar().showMessage('Export error' if is_export else 'File error · Check format and camera compatibility')
    def raw_settings(self):
        return {'white_balance':self.wb_combo.currentText().lower(),
                'highlight_mode':self.highlight_combo.currentText().lower()}
    def redecode_raw(self):
        if not self.filepath or Path(self.filepath).suffix.lower() not in engine.RAW_EXTENSIONS:return
        self.raw_options=self.raw_settings()
        self.open_path(self.filepath,preserve_edits=True)
    def schedule(self):
        if self.image_data is not None:
            self.version+=1
            self.timer.start()
    def render_debounced(self):
        if self.image_data is None or self._close_pending:return
        if self.render_thread is not None and self.render_thread.isRunning():
            self.timer.start(100);return
        self.render_thread=RenderJob(self.image_data,self.settings,self.geometry,self.linear,self.version,self.album_id,self.era_id,self.level_id)
        self.render_thread.ready.connect(self.preview_ready)
        self.render_thread.error.connect(lambda e,v:self.statusBar().showMessage('Render error · '+e) if v==self.version else None)
        self.render_thread.finished.connect(self._finish_pending_close)
        self.render_thread.start()
    def preview_ready(self,arr,version):
        if version!=self.version:return
        self.current_preview=arr
        self.hist.set_image(arr)
        self.show_image(self.cached_original if self.original_visible else arr)
    def show_image(self,arr):
        if arr is None:return
        h,w=arr.shape[:2]
        qimg=QImage(arr.data,w,h,w*3,QImage.Format_RGB888).copy()
        self.canvas.set_picture(qimg)
    def toggle_original(self):
        self.original_visible=not self.original_visible
        self.before_btn.setChecked(self.original_visible)
        self.before_btn.setText('Original Shown' if self.original_visible else 'Before / After')
        self.show_image(self.cached_original if self.original_visible else self.current_preview)
    def export_dialog(self):
        if not self.filepath:return
        suggested=str(Path(self.filepath).with_name(Path(self.filepath).stem+'_elsewhere.tif'))
        path,chosen=QFileDialog.getSaveFileName(self,'Export your edited photograph',suggested,
            '16-bit TIFF (*.tif);;16-bit PNG (*.png);;JPEG 8-bit (*.jpg)')
        if not path:return
        ext=Path(path).suffix.lower()
        if ext not in ('.tif','.tiff','.png','.jpg','.jpeg'):
            path+=('.tif' if 'TIFF' in chosen else '.png' if 'PNG' in chosen else '.jpg')
        if Path(path).resolve()==Path(self.filepath).resolve():
            QMessageBox.warning(self,'Protect original photograph',
                'The export filename matches the original photo. Choose a different filename to preserve the source.')
            return
        self.busy('Exporting full-resolution photograph…')
        job=IOJob('export',path,self.settings,self.geometry,
                  {'source':self.filepath,**self.raw_options},album_id=self.album_id,era_id=self.era_id,level_id=self.level_id)
        job.exported.connect(self.exported)
        job.error.connect(self.failed)
        self.start_job(job)
    def exported(self,path,bits):
        self.statusBar().showMessage(f'Exported · {Path(path).name} · {bits}-bit RGB')
        QMessageBox.information(self,'Export complete',
            f'Photograph exported at {bits}-bit RGB:\n{path}\n\nThe original file was not modified.')
    def save_recipe(self):
        path,_=QFileDialog.getSaveFileName(self,'Save Elsewhere recipe','elsewhere-grade.json','Elsewhere recipe (*.json)')
        if not path:return
        payload={'app':'Elsewhere Studio','version':2,'settings':self.settings,
                 'geometry':self.geometry,'raw_options':self.raw_options,'album_id':self.album_id,'era_id':self.era_id,'level_id':self.level_id}
        try:
            Path(path).write_text(json.dumps(payload,indent=2),encoding='utf-8')
            self.statusBar().showMessage('Recipe saved · '+Path(path).name)
        except OSError as e:
            QMessageBox.critical(self,'Could not save recipe',str(e))
    def load_recipe(self):
        path,_=QFileDialog.getOpenFileName(self,'Open Elsewhere recipe','','Elsewhere recipe (*.json)')
        if not path:return
        try:
            # Validate the entire recipe *before* changing UI/application state.
            if Path(path).stat().st_size>1024*1024:
                raise ValueError('Recipe file is unexpectedly large')
            payload=json.loads(Path(path).read_text(encoding='utf-8'))
            settings,geometry,raw_options,album_id,era_id=validated_recipe(payload)
            self.record_undo()
            self.settings=settings;self.geometry=geometry
            self.album_id=album_id;self.era_id=era_id
            self.level_id=payload.get('level_id','l0') if payload.get('level_id','l0') in ('l0','l1','l4','l5') else 'l0'
            self.sync_selections();self.sync_ui()
            self.raw_options=raw_options
            self.wb_combo.setCurrentText(raw_options['white_balance'].capitalize())
            self.highlight_combo.setCurrentText(raw_options['highlight_mode'].capitalize())
            if self.filepath and Path(self.filepath).suffix.lower() in engine.RAW_EXTENSIONS:
                self.open_path(self.filepath,preserve_edits=True)
            else:self.schedule()
            self.statusBar().showMessage('Recipe loaded · '+Path(path).name)
        except Exception as e:QMessageBox.critical(self,'Recipe error',str(e))
    def _finish_pending_close(self):
        if not self._close_pending:return
        if self.active_jobs or (self.render_thread is not None and self.render_thread.isRunning()):
            return
        self._close_pending=False
        self.close()
    def closeEvent(self,event):
        if self.active_jobs or (self.render_thread is not None and self.render_thread.isRunning()):
            event.ignore()
            self._close_pending=True
            self.timer.stop()
            self.statusBar().showMessage('Finishing active photo processing before closing…')
            return
        super().closeEvent(event)


def main():
    app=QApplication(sys.argv);app.setStyle('Fusion');app.setApplicationName(APP_NAME)
    if '--self-test' in sys.argv:
        import rawpy
        import cv2
        test=np.zeros((8,8,3),dtype=np.uint16)
        result=engine.render(test,out_bits=16)
        if result.shape!=(8,8,3) or result.dtype!=np.uint16:
            raise SystemExit(5)
        raise SystemExit(0)
    win=Elsewhere();win.show()
    if len(sys.argv)>1:win.open_path(sys.argv[1])
    sys.exit(app.exec())

if __name__=='__main__':main()
