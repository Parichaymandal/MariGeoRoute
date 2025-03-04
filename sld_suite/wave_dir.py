from sld import WaveDir
from sld import Currents

colors = dict(
    dark_mode='#c7c7c7',
    light_mode='#000000'
)

def create_xml(outfolder='./xml'):
    for col in colors.items():
        wave_dir = WaveDir()
        wave_dir.layer_name = f'wave_dir_{col[0]}'
        wave_dir.fill = col[1]
        wave_dir.stroke = col[1]
        wave_dir.property_name = 'GRAY_INDEX'
        wave_dir.write_sld(outfolder=outfolder)

    currents = Currents()
    currents.u = "utotal"
    currents.v = "vtotal"
    currents.write_sld(outfolder=outfolder)
