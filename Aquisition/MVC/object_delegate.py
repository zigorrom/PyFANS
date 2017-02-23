# -*- coding: utf-8 -*-
#pylint: disable-msg=C0103,C0301,W0511,C0111,C0321,W0614,W0401,W0611,W0212
"""
Created on 29.11.2010

@author: popravko
"""
from PyQt4 import QtGui, QtCore

from object_model_view_constants import ObjectModelViewConstants
from object_model_view_utils import ObjectModelViewUtils

from monument.db.data_pool import DataPool
from monument.ui.ui_utils import UiUtils
from monument.app_utils import file_icon

from dialog_editor import DialogEditorForm
from list_dialog_editor import ListDialogEditorForm

class TextEditor(QtGui.QTextEdit):
    def keyPressEvent(self, e):
        if (e.modifiers() == QtCore.Qt.ShiftModifier and e.key() == QtCore.Qt.Key_Return or
            e.modifiers() == QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_Return):
            e.ignore()
            return QtGui.QTextEdit.keyPressEvent(self, QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Return, QtCore.Qt.NoModifier))
        if e.key() == QtCore.Qt.Key_Return:
            self.clearFocus()
            e.accept()
            return

        return QtGui.QTextEdit.keyPressEvent(self, e)

class TextBrowser(QtGui.QTextBrowser):
    def __init__(self, parent = None):
        QtGui.QTextBrowser.__init__(self, parent)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.LinksAccessibleByKeyboard | QtCore.Qt.TextEditable)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)

    def keyPressEvent(self, e):
        if (e.modifiers() == QtCore.Qt.ShiftModifier and e.key() == QtCore.Qt.Key_Return or
            e.modifiers() == QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_Return):
            e.ignore()
            return QtGui.QTextEdit.keyPressEvent(self, QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Return, QtCore.Qt.NoModifier))
        if e.key() == QtCore.Qt.Key_Return:
            self.clearFocus()
            e.accept()
            return

        return QtGui.QTextEdit.keyPressEvent(self, e)


class ObjectDelegate(QtGui.QStyledItemDelegate):
    """
    Делегат предназначен для редактирования и отображения иерархических объектов,
    сопоставленных сущностям БД и полученных из sqlalchemy
    """


    def __init__(self, parent = None, classifiers = None, additionalValues = None, typeEditor = None): #IGNORE:W0102
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._classifiers = {} if not classifiers else classifiers
        self._additionalValues = {} if not additionalValues else additionalValues
        self._typeEditor = typeEditor
        self._notNullableColumns = []
        self._helpers = {
            None: NoneEditorHelper(),
            ObjectModelViewConstants.TextColumnType: TextEditorHelper(),
            ObjectModelViewConstants.HtmlTextColumnType: HtmlTextEditorHelper(),
            ObjectModelViewConstants.RestrictedTextColumnType: RestrictedTextEditorHelper(),
            ObjectModelViewConstants.ClassifierColumnType: ClassifierEditorHelper(self._classifiers, self._additionalValues),
            ObjectModelViewConstants.ImageColumnType: ImageEditorHelper(),
            ObjectModelViewConstants.NumberColumnType: NumberEditorHelper(),
            ObjectModelViewConstants.DecimalColumnType: NumberEditorHelper(decimal = True),
            ObjectModelViewConstants.DateColumnType: DateEditorHelper(),
            ObjectModelViewConstants.BooleanFlagColumnType: BooleanFlagEditorHelper(),
            ObjectModelViewConstants.CheckImageColumnType: CheckImageHelper(),
            ObjectModelViewConstants.FileFormatIconColumnType: FileEditorHelper()
            }

    def editorEvent(self, event, model, option, ind):
        return self._getHelper(ind).editor_event(self, event, model, option, ind)

    def paint(self, painter, option, ind):
        self._getHelper(ind).paint(self, painter, option, ind)

    def setNotNullableColumns(self, columnList = None):
        self._notNullableColumns = columnList if columnList is not None else []

    def createEditor(self, parent, option, index):
        return self._getHelper(index).create_editor(parent, option, index)

    def setEditorData(self, editor, index):
        return self._getHelper(index).set_editor_data(editor, index)

    def setModelData(self, editor, model, index):
        model.blockSignals(True)
        res = self._getHelper(index).set_model_data(editor, model, index)
        if res is not None and not res:
            model.blockSignals(False)
            return
        if not index.isValid():
            model.blockSignals(False)
            return
        objIndex = index
        obj = model.data(objIndex, ObjectModelViewConstants.ItemObjectRole).toPyObject()
        if obj is None:
            objIndex = index.sibling(index.row(), 0)
            obj = model.data(objIndex, ObjectModelViewConstants.ItemObjectRole).toPyObject()
            if obj is None:
                model.blockSignals(False)
                return
        # изменившиеся данные
        attrVal = model.data(index, ObjectModelViewConstants.ValueRole)
        valType = attrVal.type()
        attrVal = attrVal.toPyObject()

        if attrVal is not None:
            if valType == QtCore.QVariant.String:
                attrVal = attrVal.toLocal8Bit().data()
            # dirty workaround for QByteArray handling
            elif hasattr(attrVal, 'sanctuary'):
                attrVal = attrVal.sanctuary.data()
            elif valType == QtCore.QVariant.ByteArray:
                attrVal = attrVal.data()

        attrName = str(model.data(index, ObjectModelViewConstants.BindingRole).toPyObject())
        ObjectModelViewUtils.set_attribute(obj, attrName, attrVal)
        model.blockSignals(False)
        model.setData(objIndex, obj, ObjectModelViewConstants.ItemObjectRole)

    def sizeHint(self, option, index):
        return self._getHelper(index).size_hint(self, option, index)

    def _getHelper(self, index):

        editable = index.model().data(index, ObjectModelViewConstants.EditableRole).toPyObject()
        columnType = index.model().data(index, ObjectModelViewConstants.ColumnTypeRole).toPyObject()
        funcRoleValue = index.model().data(index, ObjectModelViewConstants.UserFuncRole).toPyObject()
        if self._typeEditor:
            columnType = self._typeEditor
            editable = True
        if funcRoleValue:
            return NoneEditorHelper(funcRoleValue)

        simple_mapped_helper = columnType in self._helpers

        if simple_mapped_helper:
            return self._helpers[columnType]
        elif columnType == ObjectModelViewConstants.DialogColumnType:
            return DialogEditorHelper()
        elif columnType == ObjectModelViewConstants.ListDialogColumnType:
            return ListDialogEditorHelper(not editable)
        else:
            return self._helpers[None]


class NoneEditorHelper(object):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0613

    def __init__(self, user_func = None):
        self._user_func = user_func

    def editor_event(self, delegate, event, model, option, ind):
        return QtGui.QStyledItemDelegate.editorEvent(delegate, event, model, option, ind)

    def paint(self, delegate, painter, option, ind):
        QtGui.QStyledItemDelegate.paint(delegate, painter, option, ind)

    def create_editor(self, parent, option, index): #IGNORE:W0613
        if self._user_func:
            self._user_func()
        return None

    def set_model_data(self, editor, model, index):
        return False

    def set_editor_data(self, editor, index):
        pass

    def size_hint(self, delegate, option, index):
        return QtGui.QStyledItemDelegate.sizeHint(delegate, option, index)


class CheckImageHelper(NoneEditorHelper):
#pylint: disable-msg=C0103  ,C0301,W0511,C0111,W0201
    def paint(self, delegate, painter, option, ind):
        checked = ind.model().data(ind, ObjectModelViewConstants.ValueRole).toPyObject()
        editable = ind.model().data(ind, ObjectModelViewConstants.EditableRole).toPyObject()
        check_box_style_option = QtGui.QStyleOptionButton()
        if editable:
            check_box_style_option.state |= QtGui.QStyle.State_Enabled

        if checked:
            check_box_style_option.state |= QtGui.QStyle.State_On
        else:
            check_box_style_option.state |= QtGui.QStyle.State_Off

        check_box_style_option.rect = BooleanFlagEditorHelper.get_check_box_rect(option)
        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_CheckBox, check_box_style_option, painter)

    @classmethod
    def get_check_box_rect(cls, view_item_style_options):
        check_box_style_options = QtGui.QStyleOptionButton()
        check_box_rect = QtGui.QApplication.style().subElementRect(
            QtGui.QStyle.SE_CheckBoxIndicator,
            check_box_style_options)
        check_box_point = QtCore.QPoint(
            view_item_style_options.rect.x() +
            view_item_style_options.rect.width() / 2 -
            check_box_rect.width() / 2,
            view_item_style_options.rect.y() +
            view_item_style_options.rect.height() / 2 -
            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())


class ImageEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0201,W0212,W0622,C0321

    PreviewNotAvailableImage = QtGui.QPixmap(':main/preview_is_not_available.png')

    class ImageDialog(QtGui.QFileDialog):


        changed = QtCore.pyqtSignal(object)
        closed = QtCore.pyqtSignal()

        def __init__(self, heritageImage, parent = None):
            decoder = QtCore.QString.fromUtf8
            cap = decoder('Выберите изображение')
            dir = decoder('')
            fltr = decoder(
                'Все поддерживаемые форматы (*.jpg *.jpeg *.bmp *.tiff *.tif *.raw);; \
                Изображения JPEG (*.jpg *.jpeg);; \
                Изображения TIFF (*.tiff *.tif);; \
                Изображения BMP (*.bmp);; \
                Необработанные файлы в формате съёмки (*.raw)')
            QtGui.QFileDialog.__init__(self, parent, cap, dir, fltr)
            self._image = heritageImage

        def show(self):
            self._accepted = False
            res = self.exec_()
            if res == QtGui.QDialog.Accepted:
                self._accepted = True
                res = True
                self._image.text = self.selectedFiles()[0]

                self.changed.emit(self._image)
                self.accept()
            else:
                self.closed.emit()
                self.reject()
            return res

    def create_editor(self, parent, option, index): #IGNORE:W0613
        item = index.model()
        objIndex = index.sibling(index.row(), 0)
        val = item.data(objIndex, ObjectModelViewConstants.ItemObjectRole).toPyObject()
        val.text = ''
        return DialogEditorForm(ImageEditorHelper.ImageDialog, val, 'text', True, parent, False)

    def set_model_data(self, editor, model, index): #IGNORE:W0613
        if editor.dialogResult() == QtGui.QDialog.Rejected: return False

        decoder = lambda qstr: qstr.toPyObject().toLocal8Bit().data() if qstr.toPyObject() is not None else None
        item = index.model()
        imageDataAttr = decoder(item.data(index, ObjectModelViewConstants.ImageDataRole))
        imageFormatAttr = decoder(item.data(index, ObjectModelViewConstants.ImageFormatAttributeRole))
        imagePreviewAttr = decoder(item.data(index, ObjectModelViewConstants.ImagePreviewAttributeRole))
        imageSmallPreviewAttr = decoder(item.data(index, ObjectModelViewConstants.ImageSmallPreviewAttributeRole))

        indexObj = index.sibling(index.row(), 0)
        obj = item.data(indexObj, ObjectModelViewConstants.ItemObjectRole).toPyObject()
#        assert ObjectModelViewUtils.test_attribute(obj, imageDataAttr)
#        assert ObjectModelViewUtils.test_attribute(obj, imagePreviewAttr)
#        assert ObjectModelViewUtils.test_attribute(obj, imageFormatAttr)

        text = editor.text()

        fi = QtCore.QFileInfo(text)
        format = fi.suffix()
        format = format.toLocal8Bit().data()
        dfs = [df for df in DataPool.document_formats.items if df.ext.lower() == format.lower()]
        if len(dfs):
            ObjectModelViewUtils.set_attribute(obj, imageFormatAttr, dfs[0].id)
        else:
            return False

        ba = QtCore.QByteArray()
        f = QtCore.QFile(text)
        f.open(QtCore.QIODevice.ReadWrite)
        ba = f.readAll()
        val = ba

        class wrapper():
            def __init__(self, data):
                self.sanctuary = data

        wrapped_val = wrapper(val)

        ObjectModelViewUtils.set_attribute(obj, imageDataAttr, val.data())
        item.setData(index, wrapped_val, ObjectModelViewConstants.ValueRole)

        pixmap = QtGui.QPixmap()
        ok = pixmap.load(text)
        if ok:
            pixmap = pixmap.scaled(
                UiUtils.compute_new_dimensions(
                    pixmap,
                    ObjectModelViewConstants.PreviewSize.width()),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)
            ba = QtCore.QByteArray()
            buffer = QtCore.QBuffer(ba)
            buffer.open(QtCore.QIODevice.WriteOnly)
            pixmap.save(buffer, format)
            ObjectModelViewUtils.set_attribute(obj, imagePreviewAttr, ba.data())

            pixmap = pixmap.scaled(
                UiUtils.compute_new_dimensions(
                    pixmap,
                    ObjectModelViewConstants.PreviewInGridSize.width()),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)
            ba = QtCore.QByteArray()
            buffer = QtCore.QBuffer(ba)
            buffer.open(QtCore.QIODevice.WriteOnly)
            pixmap.save(buffer, format)
            ObjectModelViewUtils.set_attribute(obj, imageSmallPreviewAttr, ba.data())
        else:
            pixmap = ImageEditorHelper.PreviewNotAvailableImage
            ba = QtCore.QByteArray()
            buffer = QtCore.QBuffer(ba)
            buffer.open(QtCore.QIODevice.WriteOnly)
            pixmap.save(buffer, 'PNG')
            ObjectModelViewUtils.set_attribute(obj, imagePreviewAttr, ba.data())
            ObjectModelViewUtils.set_attribute(obj, imageSmallPreviewAttr, ba.data())

        item.setData(index, pixmap, QtCore.Qt.DecorationRole)


class FileEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0201,W0212,W0622,C0321

    class FileDialog(QtGui.QFileDialog):


        changed = QtCore.pyqtSignal(object)
        closed = QtCore.pyqtSignal()

        def __init__(self, binarySemantic, parent = None, f = '*.*'):
            decoder = QtCore.QString.fromUtf8
            cap = decoder('Выберите файл')
            dir = decoder('')
            fltr = QtCore.QString.fromLocal8Bit(f)
            QtGui.QFileDialog.__init__(self, parent, cap, dir, fltr)
            self._binarySemantic = binarySemantic

        def show(self):
            self._accepted = False
            res = self.exec_()
            if res == QtGui.QDialog.Accepted:
                self._accepted = True
                res = True
                self._binarySemantic.text = self.selectedFiles()[0].toLocal8Bit().data()
                self.changed.emit(self._binarySemantic)
                self.accept()
            else:
                self.closed.emit()
                self.reject()
            return res

    def paint(self, delegate, painter, option, ind):
        option.displayAlignment = QtCore.Qt.AlignCenter
        QtGui.QStyledItemDelegate.paint(delegate, painter, option, ind)
#        if ind.model().data(ind, ObjectModelViewConstants.ValueRole).toPyObject():
#            pixmap = ind.model().data(ind, QtCore.Qt.DecorationRole)
#            pixmap = pixmap.toPyObject()
#            if pixmap is not None:
#                QtGui.QItemDelegate.drawDecoration(delegate, painter, option, option.rect, pixmap)

    def create_editor(self, parent, option, index): #IGNORE:W0613
        item = index.model()
        objIndex = index.sibling(index.row(), 0)
        val = item.data(objIndex, ObjectModelViewConstants.ItemObjectRole).toPyObject()
        val.text = ''
        acceptable_formats = item.data(index, ObjectModelViewConstants.FileAcceptableFormatsRole).toPyObject()
        if acceptable_formats is not None:
            acceptable_formats = [f.name + ' (*.' + f.ext + ')' for f in acceptable_formats]
            acceptable_formats = ';;'.join(acceptable_formats)
        return DialogEditorForm(FileEditorHelper.FileDialog, val, 'text', True, parent, False, acceptable_formats)

    def set_model_data(self, editor, model, index):
        text = QtCore.QString.fromLocal8Bit(editor.text())
        if editor.dialogResult() == QtGui.QDialog.Rejected: return False

        decoder = lambda qstr: qstr.toPyObject().toLocal8Bit().data() if qstr.toPyObject() is not None else None
        item = index.model()
        fileDataAttr = decoder(item.data(index, ObjectModelViewConstants.FileDataAttributeRole))
        fileFormatAttr = decoder(item.data(index, ObjectModelViewConstants.FileFormatAttributeRole))

        indexObj = index.sibling(index.row(), 0)
        obj = item.data(indexObj, ObjectModelViewConstants.ItemObjectRole).toPyObject()
        assert ObjectModelViewUtils.test_attribute(obj, fileDataAttr)
        assert ObjectModelViewUtils.test_attribute(obj, fileFormatAttr)

        if not text:
            return False

        fi = QtCore.QFileInfo(text)
        fileExt = fi.suffix()
        acceptableFormats = item.data(index, ObjectModelViewConstants.FileAcceptableFormatsRole)
        acceptableFormats = acceptableFormats.toPyObject()
        if acceptableFormats is not None:
            found = False
            fileFormatEntityExtAttribute = decoder(item.data(index, ObjectModelViewConstants.FileFormatEntityExtAttributeRole))
            assert fileFormatEntityExtAttribute is not None
            for format in acceptableFormats:
                assert ObjectModelViewUtils.test_attribute(format, fileFormatEntityExtAttribute)
                ext = ObjectModelViewUtils.get_attribute(format, fileFormatEntityExtAttribute)
                if ext.upper() == fileExt.toUtf8().data().upper():
                    ObjectModelViewUtils.set_attribute(obj, fileFormatAttr, format)
                    found = True
                    break
            if not found:
                codec = QtCore.QString.fromUtf8
                UiUtils.show_error_without_parent(codec('Ошибка!'), codec('Формат данного файла не поддерживается'))
                return False
        else:
            ObjectModelViewUtils.set_attribute(obj, fileFormatAttr, fileExt.toLocal8Bit().data())

        f = QtCore.QFile(text)
        f.open(QtCore.QIODevice.ReadWrite)
        ba = f.readAll()
        f.close()

        class wrapper():
            def __init__(self, data):
                self.sanctuary = data
        wrapped_val = wrapper(ba)

        ObjectModelViewUtils.set_attribute(obj, fileDataAttr, ba.data())
        item.setData(index, wrapped_val, ObjectModelViewConstants.ValueRole)
        pixmap = file_icon('.' + fileExt.toUtf8().data())
        item.setData(index, pixmap, QtCore.Qt.DecorationRole)

        return True


class TextEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111


    def create_editor(self, parent, option, index): #IGNORE:W0613
        te = TextEditor(parent)
        return te

    def set_model_data(self, editor, model, index):
        new_value = editor.toPlainText()

        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        changed = model_data != new_value

        model.setData(index, new_value, QtCore.Qt.EditRole)
        model.setData(index, new_value, QtCore.Qt.ToolTipRole)
        model.setData(index, new_value, ObjectModelViewConstants.ValueRole)

        return changed

    def set_editor_data(self, editor, index):
        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        editor.setPlainText(model_data if model_data is not None else '')
        editor.selectAll()


class HtmlTextEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111


    def paint(self, delegate, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        delegate.initStyleOption(options,index)

        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        #if (optionV4.state & QStyle::State_Selected)
        #ctx.palette.setColor(QPalette::Text, optionV4.palette.color(QPalette::Active, QPalette::HighlightedText));

        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def size_hint(self, delegate, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        delegate.initStyleOption(options,index)
        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())

    def create_editor(self, parent, option, index): #IGNORE:W0613
        te = TextBrowser(parent)
        return te

    def set_model_data(self, editor, model, index):
        new_value = editor.toHtml()

        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        changed = model_data != new_value

        model.setData(index, new_value, QtCore.Qt.EditRole)
        model.setData(index, new_value, QtCore.Qt.ToolTipRole)
        model.setData(index, new_value, ObjectModelViewConstants.ValueRole)

        return changed

    def set_editor_data(self, editor, index):
        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        editor.setHtml(model_data if model_data is not None else '')
        editor.selectAll()


class BooleanFlagEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0613 


    def paint(self, delegate, painter, option, ind):
        checked = ind.model().data(ind, ObjectModelViewConstants.ValueRole).toPyObject()
        editable = ind.model().data(ind, ObjectModelViewConstants.EditableRole).toPyObject()
        check_box_style_option = QtGui.QStyleOptionButton()
        if editable:
            check_box_style_option.state |= QtGui.QStyle.State_Enabled

        if checked:
            check_box_style_option.state |= QtGui.QStyle.State_On
        else:
            check_box_style_option.state |= QtGui.QStyle.State_Off

        check_box_style_option.rect = BooleanFlagEditorHelper.get_check_box_rect(option)
        QtGui.QApplication.style().drawControl(QtGui.QStyle.CE_CheckBox, check_box_style_option, painter)

    @classmethod
    def get_check_box_rect(cls, view_item_style_options):
        check_box_style_options = QtGui.QStyleOptionButton()
        check_box_rect = QtGui.QApplication.style().subElementRect(
            QtGui.QStyle.SE_CheckBoxIndicator,
            check_box_style_options)
        check_box_point = QtCore.QPoint(
            view_item_style_options.rect.x() +
            view_item_style_options.rect.width() / 2 -
            check_box_rect.width() / 2,
            view_item_style_options.rect.y() +
            view_item_style_options.rect.height() / 2 -
            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())

    def editor_event(self, delegate, event, model, option, ind):
        editable = ind.model().data(ind, ObjectModelViewConstants.EditableRole).toPyObject()
        if not editable: return False
        if event.type() in (QtCore.QEvent.MouseButtonRelease, QtCore.QEvent.MouseButtonDblClick):
            if (event.button() != QtCore.Qt.LeftButton or
                not BooleanFlagEditorHelper.get_check_box_rect(option).contains(event.pos())):
                return False
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() not in (QtCore.Qt.Key_Space, QtCore.Qt.Key_Select):
                return False
        else:
            return False

        if not ind.isValid():
            model.blockSignals(False)
            return False

        model.blockSignals(True)

        obj_index = ind
        obj = model.data(obj_index, ObjectModelViewConstants.ItemObjectRole).toPyObject()
        if obj is None:
            obj_index = ind.sibling(ind.row(), 0)
            obj = model.data(obj_index, ObjectModelViewConstants.ItemObjectRole).toPyObject()
            if obj is None:
                model.blockSignals(False)
                return False

        # изменившиеся данные
        attr_val = model.data(ind, ObjectModelViewConstants.ValueRole).toPyObject()
        if attr_val is None:
            return False

        attr_name = str(model.data(ind, ObjectModelViewConstants.BindingRole).toPyObject())
        ObjectModelViewUtils.set_attribute(obj, attr_name, not attr_val)
        model.setData(ind, not attr_val, ObjectModelViewConstants.ValueRole)
        model.blockSignals(False)
        return model.setData(obj_index, obj, ObjectModelViewConstants.ItemObjectRole)


class RestrictedTextEditorHelper(TextEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111


    def set_model_data(self, editor, model, index):
        notNull = index.model().data(index, ObjectModelViewConstants.notNullRole).toBool()
        new_value = editor.toPlainText().trimmed()
        if notNull and new_value.simplified().isEmpty():
            return False

        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        changed = model_data != new_value

        model.setData(index, new_value, QtCore.Qt.EditRole)
        model.setData(index, new_value, QtCore.Qt.ToolTipRole)
        model.setData(index, new_value, ObjectModelViewConstants.ValueRole)
        return changed


class NumberEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0702

    def __init__(self, decimal = False):
        NoneEditorHelper.__init__(self)
        self._decimal = decimal

    def create_editor(self, parent, option, index): #IGNORE:W0613
        if self._decimal:
            dsb = QtGui.QDoubleSpinBox(parent)
            dsb.setMinimum(0)
            dsb.setMaximum(500000)
            dsb.setSingleStep(0.1)
            dsb.setDecimals(5)
            return dsb
        else:
            sb = QtGui.QSpinBox(parent)
            sb.setMinimum(0)
            sb.setMaximum(500000)
            sb.setSingleStep(1)
            return sb

    def set_model_data(self, editor, model, index):
        new_value = editor.value()
        model.setData(index, str(new_value), QtCore.Qt.EditRole)
        model.setData(index, new_value, ObjectModelViewConstants.ValueRole)
        return True

    def set_editor_data(self, editor, index):
        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        editor.setValue(model_data if model_data else 0)


class DateEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111

    def create_editor(self, parent, option, index): #IGNORE:W0613
        dte = QtGui.QDateEdit(parent)
        UiUtils.setup_date_edit(dte)
        return dte

    def set_model_data(self, editor, model, index):
        new_value = editor.date()
        if new_value != editor.minimumDate():
            date = new_value.toPyDate()
            model.setData(index, new_value.toString("dd.MM.yyyy"), QtCore.Qt.EditRole)
            model.setData(index, date, ObjectModelViewConstants.ValueRole)
        else:
            model.setData(index, '', QtCore.Qt.EditRole)
            model.setData(index, None, ObjectModelViewConstants.ValueRole)
        return True

    def set_editor_data(self, editor, index):
        model_data = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        if model_data is not None:
            date = QtCore.QDate(model_data)
            editor.setDate(date)
        else:
            editor.setDate(editor.minimumDate())


class ClassifierEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,C0321


    def __init__(self, classifiers, additional_items):
        NoneEditorHelper.__init__(self)
        self._classifiers = classifiers
        self._additional_items = additional_items

    def create_editor(self, parent, option, index): #IGNORE:W0613
        classifier_name = index.model().data(index, ObjectModelViewConstants.TypeNameRole).toPyObject().toUtf8().data()
        assert classifier_name in self._classifiers and classifier_name in self._additional_items
        items = self._classifiers[classifier_name]
        additional_items = self._additional_items[classifier_name]
        decoder_from_local = QtCore.QString.fromLocal8Bit
        decoder_from_utf = QtCore.QString.fromUtf8
        ref_col = index.model().data(index, ObjectModelViewConstants.ReferenceAttributeRole).toPyObject().toUtf8().data()
        combo = QtGui.QComboBox(parent)
        combo.view().setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Maximum)
        combo.view().setTextElideMode(QtCore.Qt.ElideRight)
        combo.setEditable(True)
        combo.setInsertPolicy(QtGui.QComboBox.NoInsert)
        for i in range(len(additional_items)):
            combo.addItem(decoder_from_utf(additional_items[i]), -i)
        for i in items:
            assert hasattr(i, 'id') and hasattr(i, ref_col)
            combo.addItem(decoder_from_local(i.__getattribute__(ref_col)), i.id)
        return combo

    def set_model_data(self, editor, model, index):
        classifier_name = index.model().data(index, ObjectModelViewConstants.TypeNameRole).toPyObject().toUtf8().data()
        assert classifier_name in self._classifiers and classifier_name in self._additional_items
        classifier = self._classifiers[classifier_name]
        additional_items = self._additional_items[classifier_name]
        current_index = editor.currentIndex()
        if current_index == -1: return False
        new_value = editor.itemData(current_index, QtCore.Qt.EditRole).toPyObject().toLocal8Bit().data()
        new_index = editor.itemData(current_index, QtCore.Qt.UserRole).toPyObject()

        def find_in_classifier(ind):
            for i in classifier:
                assert hasattr(i, 'id')
                if i.id == ind: return i #IGNORE:C0321
            return None
        def find_in_additional(ind):
            if ind in additional_items:
                return additional_items[additional_items.index(ind)]
            return None

        decoder = QtCore.QString.fromLocal8Bit
        new_classifier_value = find_in_classifier(new_index)
        new_additional_value = None
        if new_classifier_value is None:
            new_additional_value = find_in_additional(str(decoder(new_value).toUtf8().data()))
        if new_classifier_value is not None:
            model.setData(index, new_classifier_value, ObjectModelViewConstants.ValueRole)
            model.setData(index, decoder(new_value), QtCore.Qt.EditRole)
            model.setData(index, new_index, ObjectModelViewConstants.ClassifierIndexRole)
        elif new_additional_value is not None:
            model.setData(index, None, QtCore.Qt.EditRole)
            model.setData(index, new_index, ObjectModelViewConstants.ClassifierIndexRole)
            model.setData(index, None, ObjectModelViewConstants.ValueRole)
        else: return False

        return True

    def set_editor_data(self, editor, index):
        current_index = index.model().data(index, ObjectModelViewConstants.ClassifierIndexRole).toPyObject()
        editor_index = editor.findData(current_index)
        if editor_index != -1:
            editor.setCurrentIndex(editor_index)


class DialogEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111

    def __init__(self, read_only = True):
        """
        Конструктор
        @param read_only: признак возможности прямого редактирования текстового поля
        """
        NoneEditorHelper.__init__(self)
        self._read_only = read_only

    def set_editable(self, editable):
        self._read_only = not editable

    def create_editor(self, parent, option, index): #IGNORE:W0613
        local_encoder = lambda qvar: qvar.toPyObject().toLocal8Bit().data() if qvar.toPyObject() is not None else None
        dialog_type = index.model().data(index, ObjectModelViewConstants.DialogTypeRole).toPyObject()
        ref_col = local_encoder(index.model().data(index, ObjectModelViewConstants.ReferenceAttributeRole))
        bound_object = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        view_mode_args = index.model().data(index, ObjectModelViewConstants.DialogViewModeArgsRole).toPyObject()
        return DialogEditorForm(dialog_type, bound_object, ref_col, self._read_only, parent, viewModeArgs = view_mode_args)

    def set_model_data(self, editor, model, index): #IGNORE:W0613
        decoder = QtCore.QString.fromLocal8Bit
        result = editor.result()
        text = editor.text()
        index.model().setData(index, decoder(text), QtCore.Qt.EditRole)
        index.model().setData(index, decoder(text), QtCore.Qt.ToolTipRole)
        index.model().setData(index, result, ObjectModelViewConstants.ValueRole)
        return editor.dialogResult()

    def set_editor_data(self, editor, index):
        pass


class ListDialogEditorHelper(NoneEditorHelper):
#pylint: disable-msg=C0103,C0301,W0511,C0111,W0142

    def __init__(self, readOnly = False):
        """
        Конструктор
        @param readOnly: признак возможности прямого редактирования текстового поля
        """
        NoneEditorHelper.__init__(self)
        self._readOnly = readOnly

    def create_editor(self, parent, option, index): #IGNORE:W0613
        local_encoder = lambda qvar: qvar.toPyObject().toLocal8Bit().data() if qvar.toPyObject() is not None else None
        dialog_type = index.model().data(index, ObjectModelViewConstants.DialogTypeRole).toPyObject()
        ref_col = local_encoder(index.model().data(index, ObjectModelViewConstants.ReferenceAttributeRole))
        bound_object = index.model().data(index, ObjectModelViewConstants.ValueRole).toPyObject()
        model = index.model().data(index, ObjectModelViewConstants.DialogModelRole).toPyObject()
        columns = index.model().data(index, ObjectModelViewConstants.DialogColumnsRole).toPyObject()
        multiple = index.model().data(index, ObjectModelViewConstants.DialogMultipleRole).toPyObject()
        viewModeArgs = index.model().data(index, ObjectModelViewConstants.DialogViewModeArgsRole).toPyObject()
        params = {}
        if viewModeArgs is not None:
            for k, v in viewModeArgs.iteritems():
                params[k.toUtf8().data()] = v.toUtf8().data()
        return ListDialogEditorForm(dialog_type, bound_object, ref_col, self._readOnly, parent, model, columns, multiple, **params)

    def set_model_data(self, editor, model, index): #IGNORE:W0613
        decoder = QtCore.QString.fromLocal8Bit
        result = editor.result()
        text = editor.text()
        index.model().setData(index, decoder(text), QtCore.Qt.EditRole)
        index.model().setData(index, decoder(text), QtCore.Qt.ToolTipRole)
        index.model().setData(index, result, ObjectModelViewConstants.ValueRole)
        return editor.dialogResult()

    def set_editor_data(self, editor, index):
        pass
