#Author-fastriver_org
#Description-角柱と穴を作る

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math
from . import DialogHandler as dh
from . import DataManager

app = adsk.core.Application.get()
ui = None
manager = None
if app:
    ui = app.userInterface
    manager = DataManager.Manager()
    manager.app = app
    manager.ui = ui


def run(context):
    try:
        manager.ui.messageBox('角柱を生成します')

        #ダイアログを生成
        commandDefinitions = ui.commandDefinitions
        cmdDef = commandDefinitions.itemById('Prism')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Prism',
                                                            'Create Prism',
                                                            'Create a prism.')
        onCommandCreated = dh.SampleDialogCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        dh.handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        #スクリプトが終了するのを抑制
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
