import math

class PiethonEngine:
    @staticmethod
    def calculate(expression):
        try:
            safe_dict = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'sqrt': math.sqrt,
                'pi': math.pi,
                'radians': math.radians
            }
            
            res = eval(expression, {"__builtins__": None}, safe_dict)
            
            is_pi = math.isclose(res, math.pi, rel_tol=1e-3)
            is_67 = math.isclose(res, 67, rel_tol=1e-3)
            
            return res, is_pi, is_67
        except Exception:
            return "Error", False, False