from manim_data_structures import *
from manim import *
import numpy as np


class ArrayScene(Scene):

    def construct(self):

        # arr.animate_mob_square(k).set_fill(WHITE)



        #vals = np.random.choice([0, 1], 5, p=[0.5, 0.5])

        vals = [0 for _ in range(5)]

        values = [ValueTracker(vals[k]) for k in range(5)]
        old_vals = [int(value.get_value()) for value in values]

        arr = MArray(self, vals, label="Array")
        arr.move_to(LEFT * 1)

        elements = arr.fetch_mob_arr()
        for k in range(len(vals)):
            elem = elements[k]
            #elem_index = int(elem.fetch_mob_index().text)
            #print(k, elem_index)
            elements[k].fetch_mob_square().set_fill(WHITE)
            elements[k].fetch_mob_value().set_fill(BLACK)
            #if vals[k]:
                #elements[k].fetch_mob_square().set_fill(WHITE)
                #elements[k].fetch_mob_value().set_fill(BLACK)
            #else:
                #elements[k].fetch_mob_square().set_fill(GREY_E)
                #elements[k].fetch_mob_value().set_fill(WHITE)

        #self.add(arr)
        # self.play(Write(arr))
        def update_element(elem, dt):

            elem_index = int(elem.fetch_mob_index().text)
            val = int(values[elem_index].get_value())

            #print("updating element:", type(elem), elem)
            #print("members:", dir(elem))

            # change condition, only animate if different
            if old_vals[elem_index] != val:
                if val:

                    print("setting", elem_index, "from", old_vals[elem_index], "to", val)

                    # update through elem interface
                    elem.update_mob_value(mob_value_args={'text': val, 'color': BLACK}, play_anim=False)
                    #elem.animate_mob_square().set_fill(WHITE)
                    #elem.fetch_mob_square().set_fill(WHITE)

                    # Update props of mob_square
                    #mob_square = elem.fetch_mob_square()
                    #mob_square.set_fill(WHITE)

                    # Update props of mob_label
                    #mob_square = elem.fetch_mob_square()
                    #elem._MArrayElement__update_props(mob_square_args={'color': WHITE})

                    # Remove current mob_label
                    #elem.remove(mob_square)

                    # Initialize new mob_label
                    #elem._MArrayElement__init_mobs(init_square=True)

                    # Add new mob_label to group
                    #elem.add(mob_square)

                    # update through array interface
                    #arr.update_elem_value(elem_index, val, mob_value_args={'color': 'BLACK'}, play_anim=False)
                    #arr.animate_elem_square(elem_index).set_fill(WHITE)

                else:

                    print("setting", elem_index, "from", old_vals[elem_index], "to", val)


                    # update through elem interface
                    elem.update_mob_value(mob_value_args={'text': val, 'color': BLACK}, play_anim=False)
                    #elem.update_mob_value(mob_value_args={'text': val, 'color': 'WHITE'}, play_anim=False)
                    #elem.animate_mob_square().set_fill(GREY_E)
                    #elem.fetch_mob_square().set_fill(GREY_E)

                    # Update props of mob_square
                    #mob_square = elem.fetch_mob_square()
                    #mob_square.set_fill(GREY_E)

                    # mob_square_args = elem.__mob_square_props
                    #elem._MArrayElement__update_props(mob_square_args={'color': GREY_E})

                    # Remove current mob_label
                    #elem.remove(mob_square)

                    # Initialize new mob_label
                    #elem._MArrayElement__init_mobs(init_square=True)

                    # Add new mob_label to group
                    #elem.add(mob_square)

                    # update through array interface
                    #arr.update_elem_value(elem_index, val, mob_value_args={'color': 'WHITE'}, play_anim=False)
                    #arr.animate_elem_square(elem_index).set_fill(GREY_E)

                old_vals[elem_index] = int(val)

        #MVariable

        def update_elements_in_array(arr, dt):

            elems = arr.fetch_mob_arr()

            for elem_index in range(len(values)):
                #elem_index = int(elem.fetch_mob_index().text)
                val = int(values[elem_index].get_value())
                elem = elems[elem_index]

                # change condition, only animate if different
                if old_vals[elem_index] != val:
                    if val:

                        print("setting", elem_index, "from", old_vals[elem_index], "to", val)

                        # update through elem interface
                        #elem.update_mob_value(mob_value_args={'text': val, 'color': 'BLACK'}, play_anim=False)
                        #elem.animate_mob_square().set_fill(WHITE)

                        # update through array interface
                        #arr.update_elem_value(elem_index, val, mob_value_args={'color': 'BLACK'}, play_anim=False)
                        arr.animate_elem_square(elem_index).set_fill(WHITE)

                    else:

                        print("setting", elem_index, "from", old_vals[elem_index], "to", val)

                        # update through elem interface
                        #elem.update_mob_value(mob_value_args={'text': val, 'color': 'WHITE'}, play_anim=False)
                        #elem.animate_mob_square().set_fill(GREY_E)

                        # update through array interface
                        #arr.update_elem_value(elem_index, val, mob_value_args={'color': 'WHITE'}, play_anim=False)
                        arr.animate_elem_square(elem_index).set_fill(GREY_E)

                    old_vals[elem_index] = int(val)


        #arr.add_updater(update_elements_in_array, call_updater=False)
        elems = arr.fetch_mob_arr()
        for k in range(len(vals)):
            elems[k].add_updater(update_element)
        print("added updaters")

        self.add(arr)
        print("added to scene")
#
        self.wait(1)
        print("waited 1 sec")

        for count in range(10):
            new_vals = np.random.choice([0, 1], len(values), p=[0.5, 0.5])
            old_vals = [int(value.get_value()) for value in values]
            new_anims = []
            for k in range(len(values)):
                if old_vals[k] != new_vals[k]:
                    new_anims.append(values[k].animate.set_value(int(new_vals[k])))
                #print("set_value", k, "from", old_vals[k], "to", new_vals[k])
            self.play(*new_anims, run_time=0.25)
            #self.wait(1)
            print("updated values to", new_vals)

        """
        old_vals = vals

        for count in range(10):
            new_vals = np.random.choice([0, 1], 5, p=[0.5, 0.5])
            new_anims = []
            for k in range(len(vals)):
                if old_vals[k] != new_vals[k]:
                    if new_vals[k]:
                        new_anims.append(Create(
                            arr.update_elem_value(k, new_vals[k], mob_value_args={'color': 'BLACK'}, play_anim=False)))
                        new_anims.append(arr.animate_elem_square(k).set_fill(WHITE))
                    else:
                        new_anims.append(Create(
                            arr.update_elem_value(k, new_vals[k], mob_value_args={'color': 'WHITE'}, play_anim=False)))
                        new_anims.append(arr.animate_elem_square(k).set_fill(GREY_E))

            old_vals = new_vals

            if len(new_anims) > 0:
                self.play(*new_anims, run_time=0.25)

            self.wait(0.5)
        """

        """
        self.play(Write(arr.update_elem_value(3, 0, play_anim=False, mob_value_args={'color': RED})), arr.animate_elem_square(3).set_fill(WHITE))


        # Create an array
        arr = MArray(self, [8, 7, 6, 5, 4])
        self.play(Create(arr))

        # Animate array
        self.play(arr.animate.shift(UP * 2.5 + LEFT * 5))

        # Animate array element
        self.play(arr.animate_elem(3).shift(DOWN * 0.5))
        self.play(arr.animate_elem(3).shift(UP*0.5))

        # Animate array element mobjects
        self.play(arr.animate_elem_square(0).set_fill(BLACK), arr.animate_elem_value(0).rotate(PI / 2).set_fill(RED),
                  arr.animate_elem_index(0).rotate(PI / 2))

        # Display array with hex values
        arr2 = MArray(self, [0, 2, 4, 6, 8], index_hex_display=True, index_offset=4)
        self.play(Create(arr2))
        self.play(arr2.animate.shift(DOWN * 2.5 + LEFT * 5))

        # Create customized array
        arr3 = MArray(self, [1, 1, 2], mob_square_args={'color': GRAY_A, 'fill_color': RED_E, 'side_length': 0.5},
                      mob_value_args={'color': GOLD_A, 'font_size': 28},
                      mob_index_args={'color': RED_E, 'font_size': 22})
        self.play(Create(arr3))

        # Append element
        print(type(arr2), arr2)
        arr2.append_elem(10, append_anim=GrowFromCenter)

        # Append customized element
        arr2.append_elem(12, mob_square_args={'fill_color': BLACK})
        #self.play(Write(arr2.append_elem(12, mob_square_args={'fill_color': BLACK})))

        # Update value of element
        #arr2.update_elem_value(3, 0, mob_value_args={'color': RED}, play_anim=False)
        #self.play(arr2.animate_elem_square(3).set_fill(WHITE))
        self.play(Write(arr2.update_elem_value(3, 0, play_anim=False, mob_value_args={'color': RED})), arr2.animate_elem_square(3).set_fill(WHITE))
        """
