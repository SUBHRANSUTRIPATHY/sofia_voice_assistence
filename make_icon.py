from PIL import Image

def convert_to_ico(png_path, ico_path):
    img = Image.open(png_path)
    # The sizes of the icons within the .ico file
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ico_path, format='ICO', sizes=icon_sizes)

if __name__ == "__main__":
    convert_to_ico(r"C:\Users\subhr\.gemini\antigravity\brain\06a44c1c-a41f-43f5-8e13-a49375e12e96\sofia_icon_1773797054002.png", "sofia.ico")
    print("Done")
