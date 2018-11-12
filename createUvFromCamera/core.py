# -*- coding: utf-8 -*-
import math
import maya.cmds as cmds


def get_mesh_in_selection():
    """ 選択してるものからメッシュのみ取得
    """
    mesh_object = []
    for s in cmds.ls(sl=1, type="transform"):
        if cmds.nodeType(s) == "mesh" or \
           cmds.nodeType(s) == "transform" and \
           "mesh" in [cmds.nodeType(x) for x in cmds.listHistory(s, f=1)]:
            mesh_object.append(s)
    return mesh_object


def type_camera(name):
    """ カメラかどうかを調べる
    """
    if name in cmds.listCameras(p=1):
        return True
    else:
        return False


def get_selection_camera():
    """ カメラのみを取得する
    """
    selection = cmds.ls(sl=1, type="transform")
    if not selection or selection[0] not in cmds.listCameras(p=1):
        return None
    return selection[0]


def is_horizontal(camera_name):
    """ Horizontal Fitかどうかを調べる (未使用)
    """
    filmFit = cmds.getAttr('%s.filmFit' % camera_name)
    if filmFit == 1:
        return True
    if filmFit == 2:
        return False

    if filmFit == 0:
        resoW = cmds.getAttr('defaultResolution.w')
        resoH = cmds.getAttr('defaultResolution.h')
        if float(resoW)/resoH > 1:
            return True
        else:
            return False

    if filmFit == 3:
        hFilmAperture = cmds.getAttr(
            '%s.horizontalFilmAperture' % camera_name)
        vFilmAperture = cmds.getAttr(
            '%s.verticalFilmAperture' % camera_name)
        if float(hFilmAperture)/vFilmAperture > 1:
            return True
        else:
            return False


def get_camerainfo(camera_name, horizontal_fit=True):
    """ カメラの情報を取得する
    """
    resoX = cmds.getAttr('defaultResolution.w')
    resoY = cmds.getAttr('defaultResolution.h')

    focalLength = cmds.getAttr('%s.focalLength' % camera_name)
    if horizontal_fit:
        horizontalFilmAperture = cmds.getAttr(
            '%s.horizontalFilmAperture' % camera_name)
        verticalFilmAperture = horizontalFilmAperture / resoX * resoY
    else:
        verticalFilmAperture = cmds.getAttr(
            '%s.verticalFilmAperture' % camera_name)
        horizontalFilmAperture = verticalFilmAperture / resoY * resoX

    hfov = (0.5 * horizontalFilmAperture) / (focalLength * 0.03937)
    hfov = 57.29578 * 2.0 * math.atan(hfov)

    vfov = (0.5 * verticalFilmAperture) / (focalLength * 0.03937)
    vfov = 57.29578 * 2.0 * math.atan(vfov)

    info = {'tr': cmds.xform(camera_name, q=1, ws=1, t=1),
            'ro': cmds.xform(camera_name, q=1, ws=1, ro=1),
            'angle_h': hfov,
            'angle_v': vfov,
            'aspect': resoY / (resoX * 1.0)}
    return info


def create_uv(target, camera_info):
    """ targetに対して、camera_infoの情報をもとにUVを作成する
    """
    face_num = cmds.polyEvaluate(target, face=1)
    face_name = '%s.f[0:%s]' % (target, face_num)

    attr_value = {
        'projectionCenterX': camera_info['tr'][0],
        'projectionCenterY': camera_info['tr'][1],
        'projectionCenterZ': camera_info['tr'][2],
        'rotateX': -camera_info['ro'][0],
        'rotateY': camera_info['ro'][1]+180,
        'rotateZ': -camera_info['ro'][2],
        'projectionHorizontalSweep': camera_info['angle_h'],
        'projectionVerticalSweep': camera_info['angle_v'],
        'imageScaleU': -1
    }

    projection = cmds.polyProjection(
        face_name, ch=1, type='Spherical', pcx=0, pcy=0, pcz=0)[0]

    for attr, value in attr_value.items():
        cmds.setAttr(projection + '.' + attr, value)


def create_uv_from_camera(camera_name, horizontal=True):
    """ 選択されているオブジェクトに対してcreate_uvを実行する
    """
    camera_info = get_camerainfo(camera_name, horizontal)
    selection = get_mesh_in_selection()
    for sel in selection:
        create_uv(sel, camera_info)
    cmds.select(selection)
