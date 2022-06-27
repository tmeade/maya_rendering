import nuke
import sys

def multipass_composite(
                        input_path,
                        output_path,
                        active_aovs,
                        camera_data,
                        width,
                        height,
                        start_frame,
                        end_frame,
                        background_image):

    nuke.addFormat('{} {} tmCustom'.format(width, height))
    nuke.root()['format'].setValue('tmCustom')
    nuke.root()['first_frame'].setValue(start_frame)
    nuke.root()['last_frame'].setValue(end_frame)

    nRead = nuke.nodes.Read(file=input_path)
    nRead['first'].setValue(start_frame)
    nRead['last'].setValue(end_frame)

    diffuse = active_aovs.pop(0)
    connect_from =nuke.nodes.Shuffle2(label=diffuse, inputs=[nRead])
    nuke.root().setFrame(2)

    connect_from['in1'].setValue('diffuse')

    for aov in active_aovs:
        nLayer = nuke.nodes.Shuffle2(label=aov)
        nLayer.setInput(0, nRead)
        nuke.root().setFrame(3)
        nLayer.knob('in1').setValue(aov)
        print ('LAYER: ', nLayer.channels() )

        if aov == 'emission':
            nLayer = nuke.nodes.Glow(inputs=([nLayer]))
            nLayer['tint'].setValue([1, 0.3, 0.05])
            nLayer['brightness'].setValue(8)
            nLayer['size'].setValue(25)

        nMerge = nuke.nodes.Merge()
        nMerge.setInput(1, nLayer)
        nMerge.setInput(0, connect_from)

        connect_from = nMerge

    nCam = nuke.nodes.Camera()
    load_camera_data(nCam, camera_data)

    nBackground = nuke.nodes.Read(file=background_image)

    nSphere = nuke.nodes.Sphere()
    nSphere['scaling'].setValue(1000)
    nSphere['rotate'].setValue(100, 1)
    nSphere.setInput(0, nBackground)

    nRender = nuke.nodes.ScanlineRender()
    nRender.setInput(1, nSphere)
    nRender.setInput(2, nCam)

    nAlpha = nuke.nodes.Shuffle2()
    nAlpha.setInput(0, nRead)
    nAlpha['in1'].setValue('alpha')
    nAlpha['out1'].setValue('alpha')

    final_merge = nuke.nodes.Merge2()
    final_merge.setInput(0, nRender)
    final_merge.setInput(1, nAlpha)
    final_merge.setInput(3, connect_from)

    nWrite = nuke.nodes.Write(file=output_path)
    nWrite.setInput(0, final_merge)


def load_camera_data(camera, camera_data):
    for attribute in camera_data.keys():
        camera.knob(attribute).setAnimated()
        for index in range(len(camera_data[attribute])):
            for frame in range(len(camera_data[attribute][index])):
                camera.knob(attribute).setValueAt(
                                                camera_data[attribute][index][frame],
                                                frame+1,
                                                index)



if __name__ == '__main__':
    print('Script Name: ', sys.argv[0])
    print('Arguements: ', sys.argv[1])
    data = eval(sys.argv[1])
    multipass_composite(
                        data['input_path'],
                        data['output_path'],
                        data['active_aovs'],
                        data['camera_data'],
                        data['width'],
                        data['height'],
                        data['start_frame'],
                        data['end_frame'],
                        data['background_image'])
    nuke.scriptSave(data['nuke_script_path'])
