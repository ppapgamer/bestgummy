import json
import discord
import random
import sympy
from PIL import Image, ImageOps
import re

def generate_latex(text: str, save_as = "qn.png") -> None:
        sympy.preview(text, viewer='file', filename=save_as, euler=False, dvioptions=['-D','200'])

        def get_px_color(bg_col, text_col, text_opac):
            bg_opac = 1-text_opac
            with_dec = (text_col[0]*text_opac + bg_col[0]*bg_opac, text_col[1]*text_opac + bg_col[1]*bg_opac, text_col[2]*text_opac + bg_col[2]*bg_opac, 255)
            return tuple(map(round, with_dec))
        img = Image.open(save_as)
        img = img.convert("RGBA")
        datas = img.getdata()
        bg_color = (54,57,63)
        text_color = (255,255,255)

        newData = []
        for item in datas:
            opacity = 255 - (item[0] + item[1] + item[2]) / 3
            col = get_px_color(bg_color, text_color, opacity/255)
            newData.append(col)

        img.putdata(newData)
        img = ImageOps.expand(img,border=30,fill=bg_color)
        img.save(save_as, "PNG")

        return save_as

def is_digits(s) -> bool:
    return re.match("^[0-9\/\.\-]+$", s)

def get_math_solution(txt: str) -> str:
    boxed_answer = re.search("\\\\boxed{(.+)}", txt)
    if (boxed_answer):
        z = boxed_answer.group(1).replace(" ", "")

        # fraction 
        fract = re.match("^(-?)\\\\frac{(\d+)}{(\d+)}$", z)
        if (fract):
            z = fract.group(1) + fract.group(2) + "/" + fract.group(3)
            return z
        if is_digits(z):
            return z
    return None

class QuestionGenerator():

    def __init__(self):
        with open("data/math_questions_diff.json", "r") as f:
            self.math_qns = json.load(f)

        with open("data/new_question.json", "r") as f:
            self.eng_qns = json.load(f)

    
    def get_math_question(self, difficulty="1") -> str:

        qn = random.choice(self.math_qns[difficulty])
        problem = qn["problem"]
        solution_explanation = qn["solution"]
        solution_value = get_math_solution(solution_explanation)
        return problem, solution_explanation, solution_value

    # def get_english_question(self) -> str:
    #     text = 