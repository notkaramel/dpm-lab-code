from utils import sound

def main():
    sound.play_note(note_name='A4', seconds=1, vol_factor=0.4).wait_done()

if __name__=='__main__':
    main()