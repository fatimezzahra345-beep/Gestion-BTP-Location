"""
app.py — LocationBTP | Wassime BTP
Design Premium — Interface SaaS Professionnelle
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
 page_title="LocationBTP — Wassime BTP",
 page_icon="",
 layout="wide",
 initial_sidebar_state="expanded",
)

from models import init_db
init_db()

from views_theme import LUXURY_CSS
st.markdown(LUXURY_CSS, unsafe_allow_html=True)

import controller as ctrl
import views

# Session 
if "authenticated" not in st.session_state:
 st.session_state.authenticated = False
 st.session_state.username = ""

# 
# LOGIN PAGE — Design premium blanc/bleu
# 
if not st.session_state.authenticated:
    st.markdown("""<style>
    .stApp { background:#FFFFFF !important; }
    .main .block-container { padding:0 !important; max-width:100% !important; }
    </style>""", unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1.1, 1])
    with col_c:
        st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

        # Logo
        st.markdown("""
        <div style="text-align:center;margin-bottom:24px">
            <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wgARCAEyARADASIAAhEBAxEB/8QAGwABAAMBAQEBAAAAAAAAAAAAAAQFBgMCAQf/xAAYAQEBAQEBAAAAAAAAAAAAAAAAAgEDBP/aAAwDAQACEAMQAAAC1QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOEX3h9nasUZtpOAtDZDLAAAhxaKs2Ngx43krF7TKBoACPIxzNAxTZ2rFfTf9o0nK+YXd5vczo2HvwP0LpUW89AaA49qRmW8lcwPu+wGpyr0ZYAHPAa3H7AbKxrtQ2+E9EKb8Z+dJkOuYFzrfz/fZfoZQDG6zA7HkbICyrfR+iOHeeoA8mWpO/CuQH3e5PaZQZYGczm6wtcwY2mLv26cT0Apcna1VcwYABqrzGbObBSvsM0zPCuY9GnveHeegNA+Yfc53ZzY2EqKP0X7DmT0cutKZXyVzHQm127wrfgZ632M1mVN+Vsjn1lYbYYPpyDZWdZqm3gnoPh9AiSzPzlOg1zA0uhxO2y2O1mBPA2FzTbFtri9pRzWVFRs40vpw9EeygTSsyO6i9OePTYV8/W+yeyygy0WUYDQM9mt5hK5/Az7vsBq8r1krap3AZ232X1WW5dfmVhoe3rkzvXvjy6dJUeRqvjyI3DrYZy4hejjMuuXW5BoAADEbfP7OZGwsa4e/ADuayz8+p6PPrzm0cqLI8vezgzonfl8l1FlOw40mNy6devK27c/fmB83LIdJAAARpJn518sK+uYAC+ods2wE9Hn15xRyI8jy959Rb1Fytaq1IcaTGiutpV2nWKaXEl87sx6uAAAAFBmN9gtj4NkCTvM1pssMp59ecUciPI8vefUW9RcrWqtSHGkxorraVdp1imlxJfO7MergAAAAxW1pE5RKVEVKkGmnfPs9Aa8/Y8qqRH++X0W1R78VKzrGbIjmb1tKbpc85cTvO27n09XANAAAAAAAOXWNiH4id4roh/SWhwmXKv+tnoEdlu70GbcOHDU6XT+9zRC8AAAAAAAApftyZXebMVHO7FNLnCsi3oiVl8IXycIE76AaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/9oADAMBAAIAAwAAACEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACx48AAACpIoAABZ76mAIIEAAEIKYAADoIQAWIKQAA0IJMgASMLEAA0LUAAAIIIMAKIKsACEJaEWIa0IVycIQAAAGIIFgI1dag3obEBEAAEKIAIABDeVJAEAAAAEJMJalZPH8JREAAAAEMIIkBYGpUIAAAAAAAIIIABYGhUIAAAAAAAcNckBuYtIIwMIAAAAAAABKgA0AkIyQAAAAAAAABKLKLLLGEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAgADAAAAEPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPEIhPPPPJTlvPPKEovSf/wB7zz7/AP8AvPPL/wCrz9f/AK887/8A+vPPHf8AfzzX9jzxf/8A/wD/ADh/tzzyz/vfr/vT8/Xz/wD84853/wBKv4P6+QFsz/PfPOfyv/xuC77e+HvPPPDP/v6/66Dxab6/PPPKdv8A/DyuoFSn1zzzzzzb/wD98rqDUp9888888O2kX8nOhHgyw9888888889w05853h988888888s8N9tttev8888888888888888888888888888888888888888888888888888/8QAMhEAAQQAAwcCBAUFAAAAAAAAAQACAxEEECEFEiAxM0FxExUwNFFSFEJQkfBgYYGhwf/aAAgBAgEBPwD+hGMDgvSCdGALHCIwRqvSCe3dPAxu8V6QXpBFRmjmRRrNos1nKNL4IhpeTzQyBpA3lKNbziGt5kWK4GihWUp7ZxmxlILGbBQ4JBRyYLObjZvOM0cjqiKTRZrNjt7KZzWiyVHjWSy+mz91EO+TzQ4AaQN65SCiohreUhoKM0ctoQvlk500fssC2NriIxY+p/4ocXG5xjvUIG+SlOtZDTOM2MpRpaYKGUps0rrVYfFxzi2lY3cMosFx7Dt5Kw5d6lPdrXIcgsSSJnEfVbLnfKw755Jxs3wxmjkRYrMmzadyKwxIlbX1WLJB1dut/wBlYGZhkLI20K/yVius7ytlHdjcf7r8ex0gjZrffh5IGxechoZO5FYfqt8hbU6o8LZfWPhYrrO8rAfLv/nZYPrt88UZsVnKbOTuRWH6rfIW1OqPC2X1j4WK6zvKwHy7/wCdlg+u3zxRmirCJARN65SysjaS40onhjw49isZiBiH7wFLDYg4d++Bakf6jy891hsW2GNzCOawrgyVrncrTXBwtpv4Lm7wq6TtksJtzivZ47reK9nj+4r2eP7ivZ4/uKGyIz+Yr2iL7iotmtiIe1x+FvlbxW+VvEreKDiFZRN/qv8A/8QALxEAAgECBAQFAwQDAAAAAAAAAQIRAAMEEBIhIDEzUQUUIkFxExWBMFCh8FJgYf/aAAgBAwEBPwD/AES7dZDtXmGpL5JAPC99gxArzDVafWJPBcfQJrzDV5hqExvV9ZWe2aHUoObtpUnPDtDRwYhtwMrS6mGREiKIgxlh2lYzxDbAZqYM0DObtqYnLDrsTnfWGnKw0NndbUx4LLSuV1tKk5oulQM76ys9sgYM0DImnbSpOd1NEZYZWJ2FPhmRNbViG5DK0uphwESIoiDGVhpWKxDbAZWVlqvLK5YK4tu3sJNYouR6z+Kv4R4D96II2NYddiciJEZ31hp75YdoaKvNqbLDrCzUTtV/BvaPKsLqFvnA7+9XgNHpG3c+9WRNpQe1eJWlQ+kUi6VA4b6ys9slOkyMgJ2pRpEUOdXgDbaaw4BGyyf4rFW2CanMn+KsdNfivEF1OBXlGCF324SJEURBjOwstkOdXum3xWB6Z+ax3T/NWOmvxWL6y/33rEdNuLELDTnYWFnIc6u9NvisD0z81jun+asdNfisX1V/vvWI6bcV5dS1pPagpJiKAgRkiM59Ip11KVFYeybS6SavWhdXSTSLoUL2q9hzccMDyq8C1sgUVKmD+iG07xNDxIjZQK+6Pp1RR8UeJ0ivuj+6ivuj/wCIpvE3ABgV9yubQvOnx5uehlH6X017UUBr6a0LaijbU0UB50FAj/lAAcv3X//EADoQAAEDAQQGCAQGAgMBAAAAAAECAwQABRESIAYQExQhMSIwMjM0QVFSFUJTcSNAYYGRoXKSRGJwgP/aAAgBAQABPwL/AOEJUlqKgKeNyeVfGYX1f6r4zC+r/VfGIX1f6r4xC+rUaUzJBLKwq7qZ1oMQsO2J6XK4V8fhern+tfH4Xq5/rXx6F6r/ANahTmJl+xVfd69TKlsxQC8vDfXxmF9X+q+MQvq18YhfVr4xC+r/AFUZ9EhvaNG9Oq2WN4s9xPmOIy6Ov7G0EjyX0ep0hf21oKA5I6OSwJGwtBF/ZX0ep0jf2toFI5IF2RIvUAKs9nd4bTfoOOo8RVqMbvOdR5X3jI0vZuJUPI31Hc2rCHB8wvzy3QxGccPyilqK1lR5njkQcKgR5VCe28Vtz1Gd5YbaUs+Qvp5ZcdWs81G/JYUfb2gi/sp6RyaVx+Lb4/xOXRp/awMB5tm7PpQ/giJaHNZzaLSMcZbJ5oN+fSN/ZWeUjmvhl0Vj4WFvHmrgMlrx94gOo87rxl0Yf2c0tnksZ9IX9taCgOyjhmsCRsLQRfyX0c+lL+OWlockDIkYlADzqCzu8Rpv0GQ8qtVjd5zqPK+8ZIjuxktuD5TSFY0BQ5HjllOhmO44flFOKK3FKPMm/MhWFQI8qhvbeK24PmGVRwpJPlU13by3XPU5LAY29oov7Kekc2lcfu3x/ictgv7azkeqejl0of2cMNDms9RotIxxlsnmg5bcf2FnOHzPRGXRaPgjrePNRuGa1WN4guo87rxl0UfudcZPzC8ZdIn9taBSOSOHUaPyNhaCL+yvonLpW/etpkeXSORCcSwkczUNnYRW2x8oz2uxu891PlfeMlmPbvOaX+vHJJcDLC3D8op1ZccUs8yb8jkDDZCJN3Eq/rIhWFYUOYqG7t4zbg+YZLWe2891flfcMmj8fb2gi/so6XUaVx+Db4/xOWyXtvZ7KvO6469J5Gzhhsc1nJHbLr6EDmo3U/FSqzzH8sN1LSUqKTzGuzrOenK/D4JHNRqI2mz4iW1Lvup+YpXBHAVZ5JaN9Wm9u8J1f6cKOTRePgiqdPNZyKISL1G4ZLUY3iC6jzu4UeGTRR+9DrJ8ukNekcjbWgUjk3wyaMR9pN2h5NjVb8fYWgu7sr6Q12cN3shso53X0pSlnpG+mIqnOKuCaaSlKLkcq0lQ85DCWUlQvvVdkbSVrSkczURrYRm2x8oyWk0p+C8232lC7LbLG72g6nyPEZLDf2FotnyPA6pDgZYW4eSRfTqy44pZ5qN+TR2PsYAUe05x1aUR8cVLo5oOuz0l2yGQPbQbZjcV8VUp5184WxcKjo2bYB509J2T+FQvTUyzYs8Ym+g56ip1nPw1dNN6fcNWjsfbWgknso6XVaVx70Nvjy4HIk4VAioTu3iNOeorSd/ZwtmOazkiNF+Q22PmNNpCEJSOQF2qS0H2Ftq5KF1ToD8Nf4iej7tVm4hY7ODnhpuL875pySlHRYFRsRaGPnVoeIpCig3pNMSA9+G6Ab60hiNxZSdkLgsX3VoxH2cRTp5rPVWkxvEJ1v8AThRFxuOTRd/HEW0eaDWkj+1n4BybF2TRePjlKdPJA1q7JpElDqcD6RdU+wkODaQzd/18qhhUazWwsdJI5UEvSTx4Jr8GKPcumF7RvERVoeI1Re/R960nSXJsdI5kVGaDMdtsfKLurtpjd7QcHkekMliSxElEqPRKbqeWXXVLPNRvyWBH2Fnpv7S+lrX2DqgLVtQm/hTmEIOPlS5C3ThZFwpEYJ6b6qZUlSOhyq0PEaovfo+9SI+2tlhR5ITfqxDFhv49VpVHvbbfHlwPUQWTIlNtjzNJASkJHIa19g6oPiBTqQtBB5UuQ2wMLQvNOOqcN6jUHuBVoeI1Re/R96ISkldPzSeDfCrPJLxv6q0WN4hut+ooi4kHPorHxPrePyi4ZF9g6oPiE1L7hWuD3Aq0PEaovfo+9Se4X9tVnd9+3V24xu9oODyV0hnsOPu9nt+qukci+wdUHxCameHVrg9wKtDxGqL36PvUnuF/bVZ3fft1elUfEy28Pl4HNZzG8TGm/U0BcAByyL7B1QfEJqZ4dWuD3Aq0PEaovfo+9Se4X9tVnd9+3Vz2d4iOt+opQwqIPMZdFY97jj58uAyr7B1QfEJqZ4dWuD3Aq0PEaovfo+9Se4X9tVnd9+3WW7H2FoOeiukMtjMbvZ7Y8z0jlX2Dqg+ITUzuFa4S0hgXqFTiC/w1Re/R96k9wv7arO73rNJIS5DSHGk4lprcJX0F/wAVuEr6C/4rcJX0F/xVn2Y+7KQFtqSi/iTQ4DITdzp+S2lJuN51IUUG9POlOrV2lHMDceFbdy4jFw1RHQ05eeVIeQvsq/JvlYb/AA+1S25C+0DW7O+w1uzvsNbs77DW7O+w1uzvsNbs77DW7O+w1uzvsNbs77DW7O+w1uzvsNbs77DW7O+w1u73tNRNuF3Lvw/krQbU7DcSgkKu4XUq2CiDG4/i4rl/tW9bxaRcSs7uwjEf1qyZbwnhT5OzkX4b6tpx34jhWt5DOHhgqy1pMroyHysJNyVjnSHFG8yHpSXL/IUlLYZbfEx8pKsN1OS5LFpyVt3rbRzTUR59UiVvS1J/DxcPKg42eUiX/FWeR8MJxuEceKudbRsi9MmWf2qzWXZtmC99aSF86gRHZEh9BlODZKu+9WmtCZikl+QFADgmrEcdM8pSt1bGHjj/ACZsNBkvOFXRXfcPSmrHLcBbCXRiWeKrvKpVnB2OwhtWBTXI1MgynncTcrAm7ldUSy3GpO3efxruuFGy5h/5p/ivg90NDIc4heMmo0HZTH3ioKDvlTtmlcmQ7j71GG6m7IlNoCUTLkj9Kjx1ohlpxzGo/NTdjSW0YES7k+l1WXD3KPsyrESb76gwjGfkLxX7U30iDhtJySVAhQuuuoADkP8A0/8A/8QAKhABAAEDAwMEAgIDAQAAAAAAAREAITEQIHFBgaEwUWGRwfBA4XCAsdH/2gAIAQEAAT8h/wBEJQswY2AEfB+q66IR09FAFcEmqEFWFnLMEPoky6B1dA+L9V+00gfK2JjSGyS7xTsnVg5fj0ZeScPzsuJFx39Ga0/e7EzBYKEEufdoBBw1YmPoHYyuGJQYoO8oVlaceVVsXPlJQHsxrzvd2BqZ2zsRcSn0bIDc/wBO28H/AAHfPLquDdMDAcO+bkP9eu2D93tGyKCT3BSRsmFhdzfPqRjz13RJRed98pMh5dj5EoKEEiOedglDhq3kfQOxmFxaLBUG1mbK1nTS3I+upKJthXnaeBCadm86cbLNT4Tdgv6W23qzfbZSdVwehIjIOHbATB/ZtiX4Qbre/wDQKSFHOyT1u5G2cknHnr6ECUbQmFh/4bEvRIKLpZHnckkNWdhdk7PbMjwoRBMOrmwK1kBS2N72mw2aE0L6YV50GcUsEtXekdkbJkJuPQkMx/RsLYq/MjvjWZWN2NgpyAUSiyP6oHYRHVBA+ECvnr1SvLdazsvV17jOVKWXZF7AODYrIF1cGyxN0uRQUjk2SC/ROswrX367JMszvpMhH9hoUYmFM/LU5RUsck0SxK7KkhSIwkOokygFDgQnfYMQtEuxJIqECG7TskJh/u0cWE0zOhbIsQk+OmkW+q4dcxz+VASHt1Mh8NKqnqpUsClcX6slPPjcGkEpGX49KAuWyfIhmjJZjnmodMbtsykiVjbQ0yzCjgR6Rh0Sw9r7p3BPZaEi80ms/vWTipYBr2xi/WulVjgaiR0XB6RdYZcqRAhLOycGQcNS6T9x12RS6Ll1UJ7FOHFZktSgbbzy4qJ/HflNSdvgqLyhygTWTjVBLmEfdYkx9I3qNyH+zZGOcuelZRxsTMRcfjXxdBZj0poYc12Zyh+VFAkQbFZONUiZL3zNtOmPj6UWLvtPodA7nirboQa+LToVLhZqCL3KvQV51ZONUQFmLvxUhae9Iylj0gcysc01sJZ3wPt3h2eLToGkWvnVk42p2b00KEeY3xJI85s8WnaB51ZONU89pm9NEO67TuQjF3iitgEGzxadoHnVk41Tz2mb0xq9eOaUFCQ7Yk2Pedvi052gedWTjVPPaZvUQYI85sLtTmQf2bfFpztCHCM+9KlyQY1Tz2mfj1EFphDMbBYkcMSJFqAAYMbAEoD5oTsmDSW0ULhBrOqA2NKNSiI06xRWKF9v4bFM0bufWRMREREREQLBVBHy/wAK8LZLrUEWIHWKLOlgNlFdSXlbNAEAlGb0kGYhiyrvQyWqAB33JqTvgZ6IU9STgsX2oAVnuUeaCs6jID3LKNHChbxGKLbQL0D7AjJisyqBi/8ACblBjQscnrQbAnxFGGSMdTOxCPVShJt4iKkpvU94NJmrVQY4oCEIMMUqfECkM9JZ71xdyjvJlwpknFxis4w3CsLHB/k//8QAKxABAAECBAUFAQEBAAMAAAAAAREAISAxQaEQUWFxkTCBscHw0fFAcIDh/9oACAEBAAE/EP8A0QZvnYXzr81X5qhdJ3VC/c6P2uDm9nozawZLBnX4v9r8X+0nS7//AFSXplgc45eid+cMT2Cj/Ur/AFNdH50npfdScUDalM+A6Fq9SpCl7c6mpqauHoC2V/qPQas6oGkl/wA6YIvqhbcm8UY2rKLAG0rv14qampo8lEHVqFRkDXd3eBjiENPZw+rePvxgS4Ig5Q0+I2RzS+844hXuGLVM6UOqs4FiQiDqUWpODks7zjIYuL0KdhUMuUs4NTkjKLjyxgyXQoHv9vOHNI2C5Xj7x2cpoHrO8ecVwuAvveGPOO2YZj3bJw2CJInUd48YA0wDyuFIkREYRwWyHie8ffnE1bFIhtq+njFnMqdtybxRiuWw0f1B84D+UhGq0UJEjzXd1wCSEIaaXKrWdz++MENqQzoNLNLR0STCKQzjyKVeXB5rOJugdByRoJjmDsdxwoYDEroFOBdjosbRgEV0zFuTeKMPvaoe/wBvOAs1qeMudstvjDZLtw9Z+vPoXMoG/qz84dPtjObKcAwzOn3vL8YjIDPKdYpgCDMTLBkpAF7m0+MDVmV71tX08ehaFN555bxRgyXUEdW32wFihkGrRTBkDud1xE4SJENMLoY6nzPjAsihuorNMyISJqcT8KK9CkNVanVZwSUD8uTsb4E1QIR1GjqD2Ah3ngAuGiZAAmacqS9Cx/fOCwqWUnLLeKMeau1Tk3l7/OBKFIlxNKKyG8D8R542PpY95+j3wNuFB1aF9lXRLHzSEA06Iw8QpGjwjq08y6yIVdA5VeUvuVLFharnNDZXfBYpHRVZV1wWh5y/q78YDsfJwHVwHHlMx1ihLRIR0jBnjoFdG304NXCCgHVf6eMCSW0uk7H2+1RJVrUkGUuTz88LkoZFnmaZ/HimTDzaKB1gu9qXwbUmrQ0TrSAtbvHinSgzEy4s0DQarR7gpjy3nAEY5gFeuAEWTnS6SvdT5nBrzNNosoqY0A9ilLVIXVZwar4BfR9vPC7bEZ2nePHAzKQAjl3kqKhXdftT9bt2dWo/xddaCYoyzKU5hMUS7lSRS2cs68qauelIan9RR6OYqzxo5b/OBjIEHklGATlOizuNWTxMOW79HvgCpYjHNoewMDkEcDbF4plJUqcQeS76UZlOYZyBldUhqx+Q1L+cglvajnbjzRWx0NAuTQ5FeRJ3FMJqvIDFu9Wlo6f1dnx6SkBekZC40zBCHJMF6eHv6s/NW6kIOq/0wX34jTpG0+OLnt0auwFJF3KztFDyNKajMnSSrgh1t7CiYjyM2fqjqTMByrY+G3UpxEjmijQBRHML7z6Qgjk0qNkzpm3nBMAqLyTuinNVJLzZ46lXvTdzhsPHzx3OnOpWEWW2oThKQlSi5Ei8fVR8TqNqlLJCIyrY+GzUV/DxoBujhkCQmDf0tZt4djePPoCIsSzKV/ujQByNAIOO51maW7T4gXDSU9tEt51puvUE2K376rY+GzUQIMeivUWdGedKXdyr6RRjKXQXGiSVoOiZ47ss6T9WnBudZmvkUypLRJS34b99VsfDZq32mtw9JJIq+W8i0Zt584glDVatDK8X5No84NzrM18itqU8N++q2Phs3DTm963D07is8jsbx5xBWolmgu0cQEBoFjBudZmvkVtSnhv31Wx8Nm4ac3vW4emfIoukElJCQB0Szh16VvubT5w7n8VmV8itqU8N++q2Phs3DTm963D00kSuUmotzbz5wBADNsc6PTRjW42jDufxWd3r5Fbcp4TtGs0JLESuGzcNOb3rd/UZNA+U/wCMUPlwAkc6B+3RIC9CGAQDQwNwrVQUIR0HNpZVoikskp2haLxEZL7NKuefBkkWRGpGdidOA82QKaUCd2IfUg5VByqDlUGC9pgCKUMtpNinnHij/Ip/wK/Qf2v0FfoK/QV+gr9BX6Cv0FWv4cIZFoyRyoW9jLptb/iliLHEFz4oAVOxzF572rLALpMgeenir/gxIEsjloUKIMuV0/VTY+eCXx9Vmto9B7+9TNZoAZ4TlTBIzECBDvFMbn76AkNEIp27ykjQAbLEFuXTSoWEYkp7lS/cdsQlRKvMShLn4rKDqDM3vU1A1WGneN/+ISDk1yxBF/wZamFDNcaDz5q7IPbLPzWo5BAGad61wOwgkvaavDGac9ES005HyCnLiAtOM+eVJJ7zmRNWpAWUpOzE4ZLW6VIvfcjfOgGkBAvQBmEIa7b1EQ03itefap6552P/ACf/AP/+AAMA/9k="
                 style="height:72px;object-fit:contain"/>
        </div>
        """, unsafe_allow_html=True)

        # Card unique
        st.markdown("""
        <div style="background:white;border:1px solid #DDE3EA;border-radius:10px;
                    padding:36px 32px;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div style="font-size:26px;font-weight:800;color:#0A2540;margin-bottom:4px">
                Se connecter
            </div>
            <div style="font-size:14px;color:#64748B;margin-bottom:24px">
                Accedez a votre espace Wassime BTP
            </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Nom d'utilisateur", placeholder="Admin",
                                  key="login_user")
        password = st.text_input("Mot de passe", type="password",
                                  placeholder="Votre mot de passe",
                                  key="login_pass")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        if st.button("Se connecter", width='stretch', type="primary"):
            if ctrl.verifier_mot_de_passe(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-top:20px;font-size:12px;color:#94A3B8">
            Wassime BTP · Marrakech 2026
        </div>
        """, unsafe_allow_html=True)

    st.stop()



# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
import base64 as _b64_logo
_logo_path = os.path.join(os.path.dirname(__file__), "logo_wassime_main.jpeg")
try:
    with open(_logo_path,"rb") as _lf:
        _logo_src = "data:image/jpeg;base64," + _b64_logo.b64encode(_lf.read()).decode()
except:
    _logo_src = ""

with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 16px 14px;border-bottom:1px solid #F1F5F9">
        <div style="display:flex;align-items:center;gap:10px">
            <img src="{_logo_src}"
                 style="height:38px;width:38px;object-fit:contain;border-radius:8px"/>
            <div>
                <div style="font-size:14px;font-weight:800;color:#0F172A">LocationBTP</div>
                <div style="font-size:11px;color:#94A3B8;">Wassime BTP</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:12px 16px;margin:8px 12px;background:#F8FAFC;
                border-radius:10px;border:1px solid #E2E8F0">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="width:34px;height:34px;background:#EFF6FF;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:13px;font-weight:700;color:#2563EB">MS</div>
            <div>
                <div style="font-size:13px;font-weight:700;color:#1E293B">Mr. Slimane</div>
                <div style="font-size:11px;color:#94A3B8;">Directeur General</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:4px 16px 2px">
        <div style="font-size:10.5px;font-weight:700;text-transform:uppercase;
                    letter-spacing:1px;color:#CBD5E1">Navigation</div>
    </div>
    """, unsafe_allow_html=True)

    PAGES = {
        "Tableau de Bord":      "dashboard",
        "Parc d'Engins":        "engins",
        "Commandes":            "commandes",
        "Clients":              "clients",
        "Devis":                "devis",
        "Bons de Livraison":    "livraison",
        "Attachements":         "attachements",
        "Facturation":          "facturation",
        "Suivi des Paiements":  "paiements",
        "Attestations Retard":  "attestations",
        "Calendrier":           "calendrier",
        "Parametres":           "admin",
    }

    page = st.radio("nav", list(PAGES.keys()), label_visibility="collapsed")
    page_key = PAGES[page]

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #F1F5F9;margin:0 12px'>",
                unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("Se deconnecter", width='stretch', key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

    st.markdown("""
    <div style="padding:12px 16px 8px;text-align:center">
        <div style="font-size:11px;color:#CBD5E1">LocationBTP v2.0</div>
    </div>
    """, unsafe_allow_html=True)

# ── Routing ──────────────────────────────────────────────────────────────────
import views
dispatch = {
    "dashboard":    views.render_dashboard,
    "engins":       views.render_engins,
    "commandes":    views.render_commandes,
    "clients":      views.render_clients,
    "devis":        views.render_devis,
    "livraison":    views.render_livraison,
    "attachements": views.render_attachements,
    "facturation":  views.render_facturation,
    "paiements":    views.render_paiements,
    "attestations": views.render_attestations,
    "calendrier":   views.render_calendrier,
    "admin":        views.render_admin,
}
dispatch[page_key]()
