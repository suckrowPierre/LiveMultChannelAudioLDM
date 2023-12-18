from pyo import *
import audioldm2
from multiprocessing import Process, Manager
import time
import random

class AudioGenerator:
    def __init__(self, interface_name="Quantum 2626"):
        self.interface_name = interface_name
        self.out_device_index = self.get_out_device_number(interface_name)

    def get_out_device_number(self, name):
        outs = pa_get_output_devices()
        return outs[1][outs[0].index(name)]

    def get_position_from_mapping(self, buffer_mapping, index):
        positions = []
        for i in range(len(buffer_mapping)):
            if buffer_mapping[i] == index:
                positions.append(i)
        return positions

    def get_total_number_of_elements(self, nested_list):
        total = 0
        number_of_audio_events = len(nested_list)
        for i in range(number_of_audio_events):
            total += len(nested_list[i])
        return total

    def generated_audio_for_prompt(self, pipe, prompt):
        parameters = audioldm2.generate_params(prompt)
        generated_audio = audioldm2.text2audio(pipe, parameters)
        return generated_audio

    def generated_audio_for_prompts(self, nested_prompts, audio_buffer, buffer_mapping):
        pipe = audioldm2.setup_pipeline()
        prompts_copy = [elements[:] for elements in nested_prompts]

        i = 0
        b = 0
        old_length = len(prompts_copy)
        while self.get_total_number_of_elements(prompts_copy) > 0 and i >= 0:
            prompt = prompts_copy[i].pop()
            if len(prompts_copy[i]) == 0:
                prompts_copy.pop(i)
            generated_audio = self.generated_audio_for_prompt(pipe, prompt)
            audio_buffer.append(generated_audio)
            buffer_mapping.append(b)

            if len(prompts_copy) == 0:
                break
            i = (i + 1) % len(prompts_copy)
            b = (b + 1) % old_length

        print("finished generating audio for prompts")
        print(audio_buffer)
        print(buffer_mapping)

    def play_sound(self, audio_buffer, buffer_mapping, index, channel, set_min_interval_distance, set_max_interval_distance):
        while len(audio_buffer) < 4:
            time.sleep(0.1)

        print("playing sound " + str(index))

        s = Server(sr=44100, nchnls=8, buffersize=512, duplex=0)
        s.setOutputDevice(self.out_device_index)
        s.boot()

        while True:
            audio_position = self.get_position_from_mapping(buffer_mapping, index)
            random_index = random.randint(0, len(audio_position) - 1)
            print(random_index)
            audio_list = audio_buffer[audio_position[random_index]].tolist()

            table = DataTable(size=len(audio_list), chnls=1)
            table.replace(audio_list)

            table_read_freq = 16000 / float(len(audio_list))
            reader = TableRead(table, freq=table_read_freq, loop=False, mul=0.1).out(chnl=channel)
            s.start()
            random_interval = random.randint(set_min_interval_distance, set_max_interval_distance)
            duration = len(audio_list) / 16000 + random_interval
            time.sleep(duration)
            reader.stop()
            s.stop()

    def start_generation_process(self, prompts_list):
        with Manager() as manager:
            prompts = manager.list()
            audio_buffer = manager.list()
            buffer_mapping = manager.list()

            for prompts_element in prompts_list:
                prompts.append(prompts_element)

            processes = []
            processes.append(
                Process(target=self.generated_audio_for_prompts, args=(prompts, audio_buffer, buffer_mapping)))
            processes[0].start()

            for i in range(len(prompts)):
                p = Process(target=self.play_sound, args=(audio_buffer, buffer_mapping, i, i, 10, 20))
                processes.append(p)
                p.start()

            for p in processes:
                p.join()

def main():
    prompts = [['A calm lake surface barely moving with delicate ripples', 'Gentle lapping of water against a stone wall in a serene setting', 'Subtle splashes as the occasional fish breaches the surface of the lake', 'A tranquil water scene at dusk with the sound of water caressing the shore', 'Soft murmurs of the lake water under a star-lit sky', 'Muffled sounds of water flowing around pebbles and reeds', 'Nighttime by the lake with echoes of water against a quiet backdrop', 'Isolated sounds of droplets from a nearby tree falling into the placid lake', 'The hushed tones of water in the distance as it moves slowly', 'Soothing, rhythmic motions of the lake whispering against the wall'], ['A light and unpredictable rustling of leaves in a gentle night breeze', 'Intermittent shivers of tree branches on a chilled evening', 'The quiet susurrus of foliage, sporadically disrupted by the wind', 'Whispers of leaves dancing to the rhythm of a soft wind by the lakeside', 'Trees casting shadows on the promenade, accompanied by the rustle of nature', 'Subdued rustling of leaves, setting a contemplative mood by the lake', 'Slight sways of trees, filling the silence with their leafy language', 'Nighttime rustlings on a lonely lakeside path lined with trees', 'The sound of trembling leaves, as if reacting to a profound thought', 'A symphony of leaves, orchestrated by the occasional breeze at nightfall'], ['The distant approach of footsteps nearing on old cobblestone', "The steady cadence of a friend's walk echoing through an empty promenade", 'Footsteps of a companion drawing closer, growing clearer amidst the quiet of the night', 'An impending sense of revelation with each step taken on the lakeside path', "Echoes of a friend's boots striking the path, announcing their arrival", "Soft thuds of your best friend's approach, interrupting the night's calm", "The rhythm of footsteps on stone that changed a life's path", "Anticipatory beats of a friend's arrival, paving the way for a new journey", 'Footsteps that resonate with the gravity of an important decision', 'The measured pace of a life-changing encounter, heard in the approach on a promenade'], ['The chill of an evening breeze casting a shiver across the water', 'A whispering wind that carries the weight of future decisions', 'The rush of cold air accentuating the solitude of a winter evening', "A gust of cooled breath from the water's surface, stirring thoughts and leaves alike", "Temperature's drop captured in a breeze passing over reflective waters", "The wind's caress, comforting a soul in moments of uncertainty", "A brisk wind that speaks to the advent of change in one's life", 'Windswept night evoking introspective thoughts by a chilly lakeside', 'The brush of a cold zephyr nudging towards unknown possibilities', 'The embrace of cool air around a contemplative figure sitting by the lake']]
    audio_gen = AudioGenerator("Externe Kopfhörer")
    audio_gen.start_generation_process(prompts)

if __name__ == "__main__":
    main()
