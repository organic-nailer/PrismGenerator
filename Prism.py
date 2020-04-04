
import adsk.core
import adsk.fusion
import adsk.cam
import traceback
from . import DataManager

newComp = None


def createNewComponent(app):
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component


class Prism:
    def __init__(self):
        self._prismName = "hoge"
        self._height = 1
        self._width = 1
        self._length = 10
        self._thickness = 0.1
        self._holeA = ""
        self._holeB = ""

    @property
    def prismName(self):
        return self._prismName

    @prismName.setter
    def prismName(self, value):
        self._prismName = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, value):
        self._thickness = value

    @property
    def holeA(self):
        return self._holeA

    @holeA.setter
    def holeA(self, value):
        self._holeA = value

    @property
    def holeB(self):
        return self._holeB

    @holeB.setter
    def holeB(self, value):
        self._holeB = value

    def build(self, app, ui):
        #コンポーネントの取得
        global newComp
        newComp = createNewComponent(app)
        if newComp is None:
            ui.messageBox('New component failed to create',
                          'New Component Failed')
            return

        #XY平面のスケッチを開始
        sketches = newComp.sketches
        sketch = sketches.add(newComp.xYConstructionPlane)

        #四角を2つ書く(回の字にね)
        lines = sketch.sketchCurves.sketchLines
        recLines = lines.addCenterPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(self._height/2, self._width/2, 0)
        )
        recLines = lines.addCenterPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(
                self._height/2 - self._thickness, self._width/2 - self._thickness, 0)
        )

        #外側の平面を選択
        prof = sketch.profiles.item(0)

        #押し出し距離
        distance = adsk.core.ValueInput.createByReal(self._length)

        # 押し出す
        extrudes = newComp.features.extrudeFeatures
        ext = extrudes.addSimple(
            prof,
            distance,
            adsk.fusion.FeatureOperations.NewComponentFeatureOperation
        )

        #穴あけA
        createHoles(
            newComp,
            "A",
            self._width/2.0,
            self._height,
            self._holeA,
            extrudes
        )

        #穴あけB
        createHoles(
            newComp,
            "B",
            self._height/2.0,
            self._width,
            self._holeB,
            extrudes
        )

# comp: コンポーネント
# plane: AかB
# distance: 中心から平面までの距離(cm)
# width: 平面の幅(cm)
# rawText: 入力された情報(mm)


def createHoles(comp, plane, distance, width, rawText, extrudes):
    #平面の設定
    planes = comp.constructionPlanes
    planesInput = planes.createInput()
    offset = adsk.core.ValueInput.createByReal(distance)
    planeXYZ = comp.xZConstructionPlane if plane == "A" else comp.yZConstructionPlane
    planesInput.setByOffset(
        planeXYZ,
        offset
    )
    planeA = planes.add(planesInput)

    #スケッチの開始
    sketch = comp.sketches.add(planeA)

    holesRaw = rawText.replace(" ", "").split(',')

    #DataManager.Manager().ui.messageBox("holesRaw: " + str(holesRaw))

    holes = []

    for holeRaw in holesRaw:
        if not holeRaw:
            continue
        if holeRaw[0] == '(' and holeRaw[-1] == ')':
            holeContentRaw = holeRaw[1:-1]
            holeContents = holeContentRaw.split(':')
            if len(holeContents) != 3:
                continue
            holes.append({
                "radius": float(holeContents[0]) if holeContents[0] else 3.2,
                "x": float(holeContents[1]) if holeContents[1] else width * 5,
                "y": float(holeContents[2]) if holeContents[2] else 5,
            })

    for hole in holes:
        #DataManager.Manager().ui.messageBox("穴: " + str(hole["radius"]) + "," + str(hole["x"]) + "," + str(hole["y"]))
        if plane == "A":
            sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(
                    hole["x"]/10.0 - width/2.0, -hole["y"] / 10.0, 0),
                hole["radius"]/20.0
            )
        else:
            sketch.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(-hole["y"] /
                                         10.0, hole["x"]/10.0 - width/2.0, 0),
                hole["radius"]/20.0
            )

    if len(holes) != len(sketch.profiles):
        return

    for i in range(len(holes)):
        extrudes.addSimple(
            sketch.profiles.item(i),
            adsk.core.ValueInput.createByReal(-distance*2.0),
            adsk.fusion.FeatureOperations.CutFeatureOperation
        )
