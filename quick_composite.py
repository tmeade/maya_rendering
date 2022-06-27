import os
import subprocess
import maya.cmds as cmds
import mtoa.aovs as aovs

import pprint

NUKE = '/Applications/Nuke13.1v1/Nuke13.1v1.app/Contents/MacOS/Nuke13.1'
MODULUS = 25.39999962
# Data
# This is temporary!  This data will eventually be queried from a user interface.
OUTPUT_NAME = 'test'
MAYA_RENDER_PATH = '/Users/tmeade/Documents/Maya/projects/flyby/images/'
NUKE_RENDER_PATH = '/Users/tmeade/Documents/Maya/projects/flyby/comp/'
NUKE_PYTHON_SCRIPT = '/Users/tmeade/.nuke/multipass_composite.py'
ACTIVE_AOVS = ['diffuse', 'specular', 'transmission', 'emission']
CAMERA_NAME = 'camera1'
START_FRAME = 1
END_FRAME = 2
WIDTH = cmds.getAttr('defaultResolution.width')
HEIGHT = cmds.getAttr('defaultResolution.height')
BACKGROUND_IMAGE = '/Users/tmeade/Documents/Maya/projects/flyby/sourceimages/space_pano_hdr.exr'

def main():
    data = {
            'output_name': OUTPUT_NAME,
            'maya_render_path': MAYA_RENDER_PATH,
            'nuke_render_path': NUKE_RENDER_PATH,
            'nuke_python_script': NUKE_PYTHON_SCRIPT,
            'active_aovs': ACTIVE_AOVS,
            'camera_name': CAMERA_NAME,
            'start_frame': START_FRAME,
            'end_frame': END_FRAME,
            'width': WIDTH,
            'height': HEIGHT,
            'background_image': BACKGROUND_IMAGE
            }
    quick_composite(data)


def setup_aovs(enable_aovs=['diffuse', 'specular', 'transmission', 'emission']):
    active_aovs = list()
    for aov in enable_aovs:
        active_aovs.append(aovs.AOVInterface().addAOV(aov))

    return active_aovs

def setup_render_attributes(data):
    cmds.setAttr('defaultRenderGlobals.startFrame', data['start_frame'])
    cmds.setAttr('defaultRenderGlobals.endFrame', data['end_frame'])
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', data['output_name'], type='string')
    cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', True)
    cmds.setAttr('defaultArnoldRenderOptions.imageFormat', 'exr', type='string')
    cmds.setAttr('defaultArnoldDriver.mergeAOVs', True)
    cmds.setAttr('defaultResolution.width', data['width'])
    cmds.setAttr('defaultResolution.height', data['height'])


def get_camera_data(camera_name, start_frame, end_frame):
    camera_data = {
                    'translate': [[], [], []],
                    'rotate': [[], [], []],
                    'focal': [[]],
                    'haperture': [[]],
                    'vaperture': [[]]}
    for frame in range(start_frame, end_frame):
        cmds.currentTime(frame, edit=True)

        translate = cmds.xform(camera_name, q=True, ws=True, t=True)
        rot = cmds.xform(camera_name, q=True, ws=True, ro=True)
        focal = cmds.camera(camera_name, q=True, fl=True)
        hfa = cmds.camera(camera_name, q=True, hfa=True)*MODULUS
        vfa = cmds.camera(camera_name, q=True, vfa=True)*MODULUS

        for i in range(len(translate)):
            camera_data['translate'][i].append(translate[i])
        for i in range(len(rot)):
            camera_data['rotate'][i].append(rot[i])
        camera_data['focal'][0].append(focal)
        camera_data['haperture'][0].append(hfa)
        camera_data['vaperture'][0].append(vfa)

    return camera_data

def quick_composite(data):
    print(data)

    # Create AOVs
    setup_aovs()

    # Set Maya render attributes
    setup_render_attributes(data)

    # Get Camera data
    data['camera_data'] = get_camera_data(
                                    data['camera_name'],
                                    data['start_frame'],
                                    data['end_frame'])
    # Get FX Data

    # Render image sequence in MAYA
    file_sequence_name = '{}.####.exr'.format(data['output_name'])
    maya_file_sequence = os.path.join(data['maya_render_path'], file_sequence_name)
    # cmds.arnoldRender(
    #                 width=data['width'],
    #                 height=data['height'],
    #                 camera=data['camera_name'],
    #                 batch=True)

    # Build Nuke Script
    # Define data for Nuke Script
    nuke_script_name = '{}.nk'.format(data['output_name'])
    nuke_script_path = os.path.join(data['nuke_render_path'], nuke_script_name)
    nuke_file_sequence = os.path.join(data['nuke_render_path'], file_sequence_name)
    data['nuke_script_path'] = nuke_script_path
    data['input_path'] = maya_file_sequence
    data['output_path'] = nuke_file_sequence
    # Start a new process to generate the Nuke script.
    nuke_script_process = subprocess.Popen(
                            [NUKE, '-ti', data['nuke_python_script'], str(data)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = nuke_script_process.communicate()
    pprint.pprint (stdout)
    pprint.pprint (stderr)


    # Render Nuke composite
    # render_process = subprocess.Popen(
    #                     [NUKE, '-ti', '-x', nuke_script_path],
    #                     stdout=subprocess.PIPE,
    #                     stderr=subprocess.PIPE)
    # stdout, stderr = render_process.communicate()
    # print (stdout, stderr)
