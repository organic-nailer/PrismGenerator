
import adsk.core
import adsk.fusion
import adsk.cam
import traceback
from . import Prism
from . import DataManager

manager = DataManager.Manager()

handlers = []


class SampleDialogDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if manager.ui:
                manager.ui.messageBox(
                    'Failed:\n{}'.format(traceback.format_exc()))


class SampleDialogCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            #ダイアログの設定
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = SampleDialogExecuteHandler()
            cmd.execute.add(onExecute)

            onExecutePreview = SampleDialogExecuteHandler()
            cmd.executePreview.add(onExecutePreview)

            onDestroy = SampleDialogDestroyHandler()
            cmd.destroy.add(onDestroy)

            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #inputを設定
            inputs = cmd.commandInputs

            inputs.addValueInput(
                "length",
                "角柱長さ",
                "cm",
                adsk.core.ValueInput.createByReal(10)
            )

            inputs.addValueInput(
                "height",
                "幅A",
                "cm",
                adsk.core.ValueInput.createByReal(1)
            )

            inputs.addValueInput(
                "width",
                "幅B",
                "cm",
                adsk.core.ValueInput.createByReal(1)
            )

            inputs.addValueInput(
                "thickness",
                "厚み",
                "cm",
                adsk.core.ValueInput.createByReal(0.1)
            )

            inputs.addStringValueInput(
                "_description",
                "説明",
                "(穴直径[mm]:水平位置(省略で中央)[mm]:垂直位置(省略で5mm)[mm]),(..."
            )

            inputs.addStringValueInput(
                "hole_height_side",
                "穴A",
                ""
            )

            inputs.addStringValueInput(
                "hole_width_side",
                "穴B",
                ""
            )

        except:
            if manager.ui:
                manager.ui.messageBox(
                    'Failed:\n{}'.format(traceback.format_exc()))


class SampleDialogExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs

            unitsMgr = manager.app.activeProduct.unitsManager

            prism = Prism.Prism()

            #ダイアログの入力値をPrismクラスにセットする
            prism.length = unitsMgr.evaluateExpression(inputs.itemById("length").expression, "cm")
            prism.height = unitsMgr.evaluateExpression(inputs.itemById("height").expression, "cm")
            prism.width = unitsMgr.evaluateExpression(inputs.itemById("width").expression, "cm")
            prism.thickness = unitsMgr.evaluateExpression(inputs.itemById("thickness").expression, "cm")
            prism.holeA = inputs.itemById("hole_height_side").value
            prism.holeB = inputs.itemById("hole_width_side").value

            #角柱の生成
            prism.build(manager.app, manager.ui)

            args.isValidResult = True
        except:
            if manager.ui:
                manager.ui.messageBox(
                    'Failed:\n{}'.format(traceback.format_exc()))
