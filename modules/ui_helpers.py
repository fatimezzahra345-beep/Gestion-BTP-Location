"""pages/ui_helpers.py — Composants UI partagés"""
import streamlit as st

PRIMARY="#2563EB"; GREEN="#10B981"; RED="#EF4444"; ORANGE="#F59E0B"
PURPLE="#8B5CF6"; GRAY_900="#0F172A"; GRAY_500="#64748B"
GRAY_400="#94A3B8"; GRAY_200="#E2E8F0"
BRUN="#1E3A5F"; OR="#2563EB"; VERT="#10B981"; ROUGE="#EF4444"

def _sec(title):
    st.markdown(f'<div style="font-size:11px;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:1px;color:{GRAY_500};padding:4px 0 6px;margin-top:8px;'
                f'border-bottom:1px solid {GRAY_200}">{title}</div>', unsafe_allow_html=True)

def _info(msg):
    st.markdown(f'<div style="background:#EFF6FF;border-left:4px solid {PRIMARY};'
                f'border-radius:0 8px 8px 0;padding:10px 14px;font-size:13px;'
                f'color:#1E40AF">{msg}</div>', unsafe_allow_html=True)

def _warn(msg):
    st.markdown(f'<div style="background:#FFFBEB;border-left:4px solid {ORANGE};'
                f'border-radius:0 8px 8px 0;padding:10px 14px;font-size:13px;'
                f'color:#92400E">{msg}</div>', unsafe_allow_html=True)

def _err(msg):
    st.markdown(f'<div style="background:#FEF2F2;border-left:4px solid {RED};'
                f'border-radius:0 8px 8px 0;padding:10px 14px;font-size:13px;'
                f'color:#991B1B">{msg}</div>', unsafe_allow_html=True)

def _div():
    st.markdown("<hr style='border:none;border-top:1px solid #F1F5F9;margin:16px 0'>",
                unsafe_allow_html=True)

def render_page_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;
                padding-bottom:16px;border-bottom:2px solid #F1F5F9">
        <div style="background:linear-gradient(135deg,{PRIMARY},{PURPLE});
                    width:44px;height:44px;border-radius:12px;display:flex;
                    align-items:center;justify-content:center;font-size:20px;
                    flex-shrink:0">{icon}</div>
        <div>
            <div style="font-size:22px;font-weight:800;color:{GRAY_900};
                        letter-spacing:-0.3px">{title}</div>
            <div style="font-size:13px;color:{GRAY_400};margin-top:2px">{subtitle}</div>
        </div>
    </div>""", unsafe_allow_html=True)