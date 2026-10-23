// Sound FX controller - disabled for a calm, professional interface
class SoundFXController {
  public enabled: boolean = false;

  public toggleAudio(): boolean {
    return false;
  }

  public playClick() {}
  public playChirp() {}
  public playScan() {}
  public playEngage() {}
}

export const soundFx = new SoundFXController();
