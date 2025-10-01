import dearpygui.dearpygui as dpg
import dearpygui
import ctypes

dpg.create_context()

with dpg.font_registry():
    font = dpg.add_font("Fonts/font2.ttf", 15 * 2, tag="ttf-font")

with dpg.window(label="Fonts") as main_window:
    dpg.add_text(default_value=f"DPG  {dearpygui.__version__}: default font.")
    dpg.add_text(default_value=f"DPG  {dearpygui.__version__}: custom ttf font.")
    dpg.bind_item_font(dpg.last_item(), "ttf-font")
ctypes.windll.shcore.SetProcessDpiAwareness(2)
dpg.create_viewport()
dpg.setup_dearpygui()
dpg.set_primary_window(main_window, True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
