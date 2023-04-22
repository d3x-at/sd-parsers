from ..prompt_info import PromptInfo
from .automatic1111 import AUTOMATIC1111Parser


class AUTOMATICStealthParser(AUTOMATIC1111Parser):
    PRIORITY = -1

    def parse(self, image):
        if image.mode != 'RGBA' or image.format != 'PNG':
            return None

        geninfo = self._read_info_from_image_stealth(image)
        if not geninfo:
            return None

        metadata = self._prepare_metadata(geninfo)
        if metadata is None:
            return None

        return PromptInfo(self.GENERATOR_ID, *metadata, {"parameters": geninfo})

    @staticmethod  # noqa: C901
    def _read_info_from_image_stealth(image):
        # read_info_from_image_stealth method (image.mode check is done in parse()) from:
        # https://github.com/ashen-sensored/sd_webui_stealth_pnginfo/blob/main/scripts/stealth_pnginfo.py

        width, height = image.size
        pixels = image.load()

        binary_data = ''
        buffer = ''
        index = 0
        sig_confirmed = False
        confirming_signature = True
        reading_param_len = False
        reading_param = False
        read_end = False
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                buffer += str(a & 1)
                pixels[x, y] = (r, g, b, 0)
                if confirming_signature:
                    if index == len('stealth_pnginfo') * 8 - 1:
                        if buffer == ''.join(format(byte, '08b') for byte in 'stealth_pnginfo'.encode('utf-8')):
                            confirming_signature = False
                            sig_confirmed = True
                            reading_param_len = True
                            buffer = ''
                            index = 0
                        else:
                            read_end = True
                            break
                elif reading_param_len:
                    if index == 32:
                        param_len = int(buffer, 2)
                        reading_param_len = False
                        reading_param = True
                        buffer = ''
                        index = 0
                elif reading_param:
                    if index == param_len:
                        binary_data = buffer
                        read_end = True
                        break
                else:
                    # impossible
                    read_end = True
                    break

                index += 1
            if read_end:
                break

        if sig_confirmed and binary_data != '':
            # Convert binary string to UTF-8 encoded text
            decoded_data = bytearray(int(binary_data[i:i + 8], 2) for i in range(
                0, len(binary_data), 8)).decode('utf-8', errors='ignore')

            return decoded_data

        return None
