import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import re
import os

# Настройка страницы
st.set_page_config(
    page_title="CRM Анализ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Применяем кастомную тему
st.markdown("""
<style>
:root {
  --background: #e8ebed;
  --foreground: #333333;
  --card: #ffffff;
  --card-foreground: #333333;
  --popover: #ffffff;
  --popover-foreground: #333333;
  --primary: #e05d38;
  --primary-foreground: #ffffff;
  --secondary: #f3f4f6;
  --secondary-foreground: #4b5563;
  --muted: #f9fafb;
  --muted-foreground: #6b7280;
  --accent: #d6e4f0;
  --accent-foreground: #1e3a8a;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: #dcdfe2;
  --input: #f4f5f7;
  --ring: #e05d38;
  --chart-1: #86a7c8;
  --chart-2: #eea591;
  --chart-3: #5a7ca6;
  --chart-4: #466494;
  --chart-5: #334c82;
  --sidebar: #dddfe2;
  --sidebar-foreground: #333333;
  --sidebar-primary: #e05d38;
  --sidebar-primary-foreground: #ffffff;
  --sidebar-accent: #d6e4f0;
  --sidebar-accent-foreground: #1e3a8a;
  --sidebar-border: #e5e7eb;
  --sidebar-ring: #e05d38;
  --font-sans: Inter, sans-serif;
  --font-serif: Source Serif 4, serif;
  --font-mono: JetBrains Mono, monospace;
  --radius: 0.75rem;
  --shadow-2xs: 0px 1px 3px 0px hsl(0 0% 0% / 0.05);
  --shadow-xs: 0px 1px 3px 0px hsl(0 0% 0% / 0.05);
  --shadow-sm: 0px 1px 3px 0px hsl(0 0% 0% / 0.10), 0px 1px 2px -1px hsl(0 0% 0% / 0.10);
  --shadow: 0px 1px 3px 0px hsl(0 0% 0% / 0.10), 0px 1px 2px -1px hsl(0 0% 0% / 0.10);
  --shadow-md: 0px 1px 3px 0px hsl(0 0% 0% / 0.10), 0px 2px 4px -1px hsl(0 0% 0% / 0.10);
  --shadow-lg: 0px 1px 3px 0px hsl(0 0% 0% / 0.10), 0px 4px 6px -1px hsl(0 0% 0% / 0.10);
  --shadow-xl: 0px 1px 3px 0px hsl(0 0% 0% / 0.10), 0px 8px 10px -1px hsl(0 0% 0% / 0.10);
  --shadow-2xl: 0px 1px 3px 0px hsl(0 0% 0% / 0.25);
  --tracking-normal: 0em;
  --spacing: 0.25rem;
}

/* Применяем цвета к элементам Streamlit */
.main .block-container {
    background-color: var(--background) !important;
}

.stApp {
    background-color: var(--background) !important;
}

/* Стили для метрик */
.kpi-card {
    background: var(--card);
    color: var(--card-foreground);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    padding: 20px 24px 16px 24px;
    margin-bottom: 24px;
    font-family: var(--font-sans);
    min-width: 240px;
    transition: box-shadow .15s;
}
.kpi-card-label {
    font-size: 1.03rem;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 6px;
}
.kpi-card-value {
    font-size: 2.05rem;
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 4px;
    margin-top: 2px;
}

/* Стили для метрик с дельтой */
.kpi-card-delta {
    background: var(--card);
    color: var(--card-foreground);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    padding: 20px 28px 18px 28px;
    font-family: var(--font-sans);
    min-width: 238px;
    margin-bottom: 18px;
    display: flex; 
    flex-direction: column;
    gap: 3px;
}
.kpi-label { 
    font-size: 1rem; 
    color: #787c8a; 
    font-weight: 500;
}
.kpi-value { 
    font-size: 2.0rem; 
    font-weight: 800; 
    color: var(--primary); 
    margin-top: 7px;
}
.kpi-delta-up {
    color: #16a34a;
    font-size: 1rem;
    margin-bottom: 3px;
    font-weight: 500;
}
.kpi-delta-blue {
    color: #3b82f6;
    font-size: 1rem;
    margin-bottom: 3px;
    font-weight: 500;
}
.kpi-delta-down {
    color: #ef4444;
    font-size: 1rem;
    margin-bottom: 3px;
    font-weight: 500;
}
.kpi-caption {
    font-size: 0.97rem;
    color: #888;
    margin-top: 4px;
}

/* Стили для заголовков */
h1, h2, h3, h4, h5, h6 {
    color: var(--foreground) !important;
}

/* Стили для текста */
p, div, span {
    color: var(--foreground) !important;
}

/* Стили для основного контейнера */
.main .block-container {
    background-color: var(--background) !important;
}
</style>
""", unsafe_allow_html=True)

# Заголовок
st.subheader("📊 CRM Анализ интересов и сделок")

st.markdown("---")

def normalize_phone(phone):
    """Нормализация телефонных номеров"""
    if pd.isna(phone):
        return None
    
    # Удаляем все нецифровые символы
    digits_only = re.sub(r'\D', '', str(phone))
    
    # Если номер начинается с '8' и состоит из 11 цифр, заменяем на '7'
    if len(digits_only) == 11 and digits_only.startswith('8'):
        digits_only = '7' + digits_only[1:]
    
    # Если начинается с '7' или '+7', оставляем как есть
    if len(digits_only) == 11 and digits_only.startswith('7'):
        return digits_only
    
    return digits_only

def classify_event_type(event_type):
    """Классификация событий"""
    if pd.isna(event_type):
        return 'Прочее'
    
    event_type = str(event_type).strip()
    
    # Замены согласно инструкции
    if event_type == 'Прочее':
        return 'Сайт'
    elif event_type in ['Почтовое письмо', 'Электронное письмо']:
        return 'Электронное письмо'
    elif event_type in ['Личная встреча', 'Телефонный звонок']:
        return 'Телефонный звонок'
    else:
        return event_type

def replace_project_values(project):
    """Замена значений в колонке 'Проект'"""
    if pd.isna(project):
        return 'Пустой'
    
    project = str(project).strip()
    
    replacements = {
        'Ангары': 'Ангары',
        'Блоки': 'Блоки', 
        'Дома': 'Ангары',
        'Кровля': 'Кровля и Фасады',
        'Снабжение': 'Кровля и Фасады',
        'Фасады': 'Кровля и Фасады',
        'Пусто (Нет данных)': 'Пустой'
    }
    
    return replacements.get(project, project)

def get_unique_interests(df):
    """Определение уникальных интересов"""
    if len(df) == 0:
        return 0
    
    # Если у всех записей нет телефонов, считаем каждую запись как уникальный интерес
    if df['Телефон_нормализованный'].isna().all():
        return len(df)
    
    # Группируем по нормализованному телефону
    df_grouped = df.groupby('Телефон_нормализованный')
    
    unique_interests = 0
    
    for phone, group in df_grouped:
        if pd.isna(phone):
            # Если телефон пустой, считаем каждую запись как уникальный интерес
            unique_interests += len(group)
        elif len(group) == 1:
            unique_interests += 1
        else:
            # Сортируем по дате
            group_sorted = group.sort_values('Дата создания')
            
            # Проверяем интервалы между событиями
            last_date = None
            for _, row in group_sorted.iterrows():
                current_date = row['Дата создания']
                
                if last_date is None or (current_date - last_date).days > 2:
                    unique_interests += 1
                    last_date = current_date
    
    return unique_interests

@st.cache_data
def load_and_process_data(uploaded_interests_file=None, uploaded_deals_file=None):
    """Загрузка и обработка данных"""
    try:
        # Загружаем данные
        if uploaded_interests_file is not None:
            interests_df = pd.read_excel(uploaded_interests_file)
        else:
            interests_df = pd.read_excel("список интересов за 2024-2025.xlsx")
            
        if uploaded_deals_file is not None:
            deals_df = pd.read_excel(uploaded_deals_file)
        else:
            deals_df = pd.read_excel("список сделок за 2024-2025.xlsx")
        
        # Обработка интересов
        interests_df['Дата создания'] = pd.to_datetime(interests_df['Дата создания'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
        
        # Фильтрация данных с 01.01.2024
        start_date = pd.to_datetime('2024-01-01')
        interests_df = interests_df[interests_df['Дата создания'] >= start_date]
        
        interests_df['Телефон_нормализованный'] = interests_df['Телефон'].apply(normalize_phone)
        interests_df['Вид события_классифицированный'] = interests_df['Вид события'].apply(classify_event_type)
        interests_df['Проект_обработанный'] = interests_df['Проект'].apply(replace_project_values)
        interests_df['Месяц'] = interests_df['Дата создания'].dt.to_period('M')
        interests_df['Месяц_год'] = interests_df['Дата создания'].dt.strftime('%Y-%m')
        
        # Обработка сделок - извлекаем дату из колонки "Ссылка"
        def extract_date_from_link(link_text):
            if pd.isna(link_text):
                return None
            
            link_text = str(link_text)
            # Ищем дату в формате "от DD.MM.YYYY HH:MM:SS"
            import re
            match = re.search(r'от (\d{1,2})\.(\d{1,2})\.(\d{4})', link_text)
            if match:
                day, month, year = match.groups()
                try:
                    return datetime(int(year), int(month), int(day))
                except:
                    return None
            return None
        
        # Извлекаем даты из колонки "Ссылка"
        deals_df['Дата_из_ссылки'] = deals_df['Ссылка (служебное поле для вывода на экран прочих реквизитов объекта)'].apply(extract_date_from_link)
        
        # Фильтрация данных с 01.01.2024
        deals_df = deals_df[deals_df['Дата_из_ссылки'] >= start_date]
        
        deals_df['Месяц'] = deals_df['Дата_из_ссылки'].dt.to_period('M')
        deals_df['Месяц_год'] = deals_df['Дата_из_ссылки'].dt.strftime('%Y-%m')
        
        return interests_df, deals_df
        
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None, None

def create_monthly_summary(interests_df, deals_df):
    """Создание сводной таблицы по месяцам"""
    if interests_df is None or deals_df is None:
        return None
    
    try:
        # Подсчет интересов по месяцам
        monthly_interests = interests_df.groupby('Месяц_год').size().reset_index(name='Количество интересов')
        
        # Подсчет уникальных интересов по месяцам
        monthly_unique_interests = []
        for month in interests_df['Месяц_год'].unique():
            month_data = interests_df[interests_df['Месяц_год'] == month]
            unique_count = get_unique_interests(month_data)
            monthly_unique_interests.append({
                'Месяц_год': month,
                'Уникальные интересы': unique_count
            })
        
        monthly_unique_df = pd.DataFrame(monthly_unique_interests)
        
        # Подсчет сделок по месяцам (используем дату из ссылки)
        monthly_deals = deals_df.groupby('Месяц_год').size().reset_index(name='Количество сделок')
        
        # Объединяем все данные
        monthly_summary = monthly_interests.merge(monthly_unique_df, on='Месяц_год', how='outer')
        monthly_summary = monthly_summary.merge(monthly_deals, on='Месяц_год', how='outer')
        
        # Заполняем NaN нулями
        monthly_summary = monthly_summary.fillna(0)
        
        # Сортируем по месяцу
        monthly_summary = monthly_summary.sort_values('Месяц_год')
        
        return monthly_summary
        
    except Exception as e:
        st.error(f"Ошибка создания сводной таблицы: {e}")
        return None

def create_monthly_chart(monthly_data):
    """Создание красивого графика с уникальными интересами и сделками"""
    if monthly_data is None or len(monthly_data) == 0:
        return None
    
    try:
        # Создаем график с двумя осями Y
        fig = go.Figure()
        
        # Сглаженная линия уникальных интересов (левая ось Y)
        fig.add_trace(go.Scatter(
            x=monthly_data['Месяц_год'],
            y=monthly_data['Уникальные интересы'],
            mode='lines+markers+text',
            name='Уникальные интересы',
            line=dict(color='#86a7c8', width=4, shape='spline'),
            marker=dict(size=10, color='#86a7c8', line=dict(width=2, color='white')),
            text=monthly_data['Уникальные интересы'],
            textposition='top center',
            textfont=dict(size=13, color='#2c3e50', weight='bold'),
            hovertemplate='<b>%{x}</b><br>Уникальные интересы: %{y}<extra></extra>',
            yaxis='y'
        ))
        
        # Линия сделок (одна ось Y)
        fig.add_trace(go.Scatter(
            x=monthly_data['Месяц_год'],
            y=monthly_data['Количество сделок'],
            mode='lines+markers+text',
            name='Количество сделок',
            line=dict(color='#eea591', width=3, shape='spline'),
            marker=dict(size=10, color='#eea591', line=dict(width=2, color='white')),
            text=monthly_data['Количество сделок'],
            textposition='bottom center',
            textfont=dict(size=12, color='#2c3e50', weight='bold'),
            hovertemplate='<b>%{x}</b><br>Количество сделок: %{y}<extra></extra>',
            yaxis='y'
        ))
        
        # Настройка макета с двумя осями Y
        fig.update_layout(
            title={
                'text': '📈 Динамика уникальных интересов и сделок за весь период',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50'}
            },
            xaxis_title="Месяц",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode='x unified',
            # Настройка одной оси Y
            yaxis=dict(
                title="Количество",
                title_font=dict(color="#2c3e50"),
                tickfont=dict(color="#2c3e50"),
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                zeroline=True,
                zerolinecolor='lightgray'
            )
        )
        
        # Настройка оси X
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Ошибка создания графика: {e}")
        return None

def create_interest_types_chart(interests_df):
    """Создание круговой диаграммы по уникальным видам интересов"""
    if interests_df is None or len(interests_df) == 0:
        return None
    
    try:
        # Подсчитываем уникальные интересы по видам событий
        unique_interests_by_type = {}
        
        for event_type in interests_df['Вид события_классифицированный'].unique():
            type_data = interests_df[interests_df['Вид события_классифицированный'] == event_type]
            
            # Для электронных писем считаем каждую запись как уникальный интерес
            if event_type == 'Электронное письмо':
                unique_count = len(type_data)
            else:
                unique_count = get_unique_interests(type_data)
            
            unique_interests_by_type[event_type] = unique_count
        
        event_type_counts = pd.Series(unique_interests_by_type)
        
        # Цвета для разных видов событий
        colors = {
            'Сайт': '#86a7c8',
            'Телефонный звонок': '#eea591', 
            'Электронное письмо': '#5a7ca6',
            'Прочее': '#466494'
        }
        
        # Создаем круговую диаграмму (donut chart)
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=event_type_counts.index,
            values=event_type_counts.values,
            hole=0.6,  # Делаем отверстие в центре для donut chart
            marker_colors=[colors.get(event_type, '#cccccc') for event_type in event_type_counts.index],
            textinfo='label+percent+value',
            textposition='outside',
            textfont=dict(size=12, color='#2c3e50'),
            hovertemplate='<b>%{label}</b><br>Уникальные интересы: %{value}<br>Процент: %{percent}<extra></extra>'
        ))
        
        # Настройка макета
        fig.update_layout(
            title={
                'text': '📊 Распределение видов интересов',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1
            ),
            margin=dict(l=50, r=150, t=80, b=50),
            showlegend=True
        )
        
        # Добавляем центральный текст с общим количеством уникальных интересов
        total_unique_interests = event_type_counts.sum()
        fig.add_annotation(
            text=f"<b>{total_unique_interests}</b><br>Уникальных интересов",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color='#2c3e50'),
            align="center"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Ошибка создания круговой диаграммы: {e}")
        return None

def create_interest_source_chart(interests_df):
    """Создание горизонтальной столбчатой диаграммы по источникам интереса"""
    if interests_df is None or len(interests_df) == 0:
        return None
    
    try:
        # Подсчитываем количество по источникам интереса
        source_counts = interests_df['Источник интереса'].value_counts()
        
        # Объединяем похожие источники
        combined_sources = {}
        
        for source, count in source_counts.items():
            # Объединяем прямые заходы
            if source in ['Прямой заход', 'Прямые заходы', '<>']:
                combined_sources['Прямые заходы'] = combined_sources.get('Прямые заходы', 0) + count
            else:
                combined_sources[source] = count
        
        # Сортируем от большего к меньшему
        sorted_sources = dict(sorted(combined_sources.items(), key=lambda x: x[1], reverse=True))
        
        # Берем топ-10 источников для лучшей читаемости
        top_sources = dict(list(sorted_sources.items())[:10])
        
        # Яркие цвета для источников (заменяем темные на яркие)
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                 '#1abc9c', '#e67e22', '#34495e', '#16a085', '#8e44ad']
        
        # Создаем горизонтальную столбчатую диаграмму
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=list(top_sources.keys()),
            x=list(top_sources.values()),
            orientation='h',
            marker_color=colors[:len(top_sources)],
            text=list(top_sources.values()),
            textposition='auto',
            textfont=dict(size=12, color='#2c3e50', weight='bold'),
            hovertemplate='<b>%{y}</b><br>Количество: %{x}<extra></extra>'
        ))
        
        # Настройка макета
        fig.update_layout(
            title={
                'text': '📊 Источники интереса',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            xaxis_title="Количество",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=False
        )
        
        # Настройка осей
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray'
        )
        
        fig.update_yaxes(
            showgrid=False,
            zeroline=False
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Ошибка создания графика источников интереса: {e}")
        return None

def create_conversion_chart(monthly_data):
    """Создание графика конверсии (отношение сделок к интересам)"""
    if monthly_data is None or len(monthly_data) == 0:
        return None
    
    try:
        # Рассчитываем конверсию
        monthly_data['Конверсия %'] = (monthly_data['Количество сделок'] / monthly_data['Уникальные интересы'] * 100).round(1)
        
        # Создаем график конверсии
        fig = go.Figure()
        
        # Столбцы конверсии
        fig.add_trace(go.Bar(
            x=monthly_data['Месяц_год'],
            y=monthly_data['Конверсия %'],
            name='Конверсия %',
            marker_color='#5a7ca6',
            opacity=0.8,
            text=monthly_data['Конверсия %'].apply(lambda x: f"{x}%" if pd.notna(x) else "0%"),
            textposition='outside',
            textfont=dict(size=11, color='#2c3e50', weight='bold'),
            hovertemplate='<b>%{x}</b><br>Конверсия: %{y:.1f}%<extra></extra>'
        ))
        
        # Настройка макета
        fig.update_layout(
            title={
                'text': '📊 Конверсия (сделки/интересы) за весь период',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            xaxis_title="Месяц",
            yaxis_title="Конверсия, %",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            hovermode='x unified'
        )
        
        # Настройка осей
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=False
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='lightgray',
            range=[0, max(monthly_data['Конверсия %'].fillna(0)) * 1.2]
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Ошибка создания графика конверсии: {e}")
        return None

def main():
    # Загрузка данных
    interests_df, deals_df = load_and_process_data()
    
    # Блок загрузки файлов (скрывающийся)
    with st.expander("📁 Загрузка файлов", expanded=False):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            uploaded_interests = st.file_uploader("📊 Загрузить файл интересов", type=['xlsx', 'xls'], key="interests_uploader")
            if uploaded_interests is not None:
                st.success(f"✅ Загружен файл: {uploaded_interests.name}")
                st.caption(f"📅 Дата загрузки: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        with col2:
            uploaded_deals = st.file_uploader("📊 Загрузить файл сделок", type=['xlsx', 'xls'], key="deals_uploader")
            if uploaded_deals is not None:
                st.success(f"✅ Загружен файл: {uploaded_deals.name}")
                st.caption(f"📅 Дата загрузки: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        # Кнопка для обновления данных
        with col3:
            if st.button("🔄 Обновить данные", type="primary", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
    
    # Загружаем данные с учетом загруженных файлов
    if uploaded_interests is not None or uploaded_deals is not None:
        interests_df, deals_df = load_and_process_data(uploaded_interests, uploaded_deals)
    
    if interests_df is not None and deals_df is not None:
        # Создаем сводную таблицу по месяцам
        monthly_summary = create_monthly_summary(interests_df, deals_df)
        
        if monthly_summary is not None:
            # Показываем общие итоги
            total_interests = monthly_summary['Количество интересов'].sum()
            total_unique_interests = monthly_summary['Уникальные интересы'].sum()
            total_deals = monthly_summary['Количество сделок'].sum()
            
            # Рассчитываем общую конверсию
            total_conversion = (total_deals / total_unique_interests * 100) if total_unique_interests > 0 else 0
            
            # Создаем карточки с использованием данных
            cards = [
                {"label": "Общее количество интересов", "value": str(total_interests)},
                {"label": "Уникальные интересы", "value": str(total_unique_interests)},
                {"label": "Количество сделок", "value": str(total_deals)},
                {"label": "Конверсия сделок к интересам, %", "value": f"{total_conversion:.1f}%"},
            ]
            
            card_cols = st.columns(4)
            for card, col in zip(cards, card_cols):
                with col:
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div class="kpi-card-label">{card['label']}</div>
                        <div class="kpi-card-value">{card['value']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            

            
            # Создаем и показываем графики
            chart = create_monthly_chart(monthly_summary)
            conversion_chart = create_conversion_chart(monthly_summary)
            interest_types_chart = create_interest_types_chart(interests_df)
            interest_source_chart = create_interest_source_chart(interests_df)
            
            if chart and conversion_chart:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.plotly_chart(chart, use_container_width=True, key="main_chart")
                with col2:
                    st.plotly_chart(conversion_chart, use_container_width=True, key="conversion_chart_main")
            
            # График видов интересов и источников интереса
            if interest_types_chart and interest_source_chart:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.plotly_chart(interest_types_chart, use_container_width=True, key="interest_types_main")
                with col2:
                    st.plotly_chart(interest_source_chart, use_container_width=True, key="interest_source_main")
            
            # Показываем таблицу под графиком (сворачиваемую)
            with st.expander("📋 Детальная таблица по месяцам"):
                st.dataframe(monthly_summary, use_container_width=True)
            
            # Разделительная линия
            st.markdown("---")
            
            # Заголовок для блока текущего года
            st.subheader("📊 Анализ за текущий год (2025)")
            st.markdown("*Сравнение с аналогичным периодом прошлого года*")
            
            # Функция для расчета метрик текущего года с сравнением
            def calculate_current_year_metrics(interests_df, deals_df):
                # Находим самую позднюю дату в данных 2025 года
                current_year_data = interests_df[interests_df['Дата создания'] >= pd.to_datetime('2025-01-01')]
                if len(current_year_data) > 0:
                    latest_date_2025 = current_year_data['Дата создания'].max()
                else:
                    latest_date_2025 = pd.to_datetime('2025-01-01')
                
                # Определяем период сравнения: с 1 января по самую позднюю дату
                current_year_start = pd.to_datetime('2025-01-01')
                current_year_end = latest_date_2025
                
                # Фильтруем данные за 2025 год (текущий период)
                current_year_interests = interests_df[
                    (interests_df['Дата создания'] >= current_year_start) & 
                    (interests_df['Дата создания'] <= current_year_end)
                ]
                current_year_deals = deals_df[
                    (deals_df['Дата_из_ссылки'] >= current_year_start) & 
                    (deals_df['Дата_из_ссылки'] <= current_year_end)
                ]
                
                # Фильтруем данные за 2024 год для сравнения (аналогичный период)
                prev_year_start = pd.to_datetime('2024-01-01')
                # Вычисляем дату окончания периода 2024 года, соответствующую текущей дате 2025
                days_diff = (current_year_end - current_year_start).days
                prev_year_end = prev_year_start + pd.Timedelta(days=days_diff)
                
                prev_year_interests = interests_df[
                    (interests_df['Дата создания'] >= prev_year_start) & 
                    (interests_df['Дата создания'] <= prev_year_end)
                ]
                prev_year_deals = deals_df[
                    (deals_df['Дата_из_ссылки'] >= prev_year_start) & 
                    (deals_df['Дата_из_ссылки'] <= prev_year_end)
                ]
                
                # Рассчитываем метрики текущего года
                current_interests = len(current_year_interests)
                current_unique_interests = get_unique_interests(current_year_interests)
                current_deals = len(current_year_deals)
                current_conversion = (current_deals / current_unique_interests * 100) if current_unique_interests > 0 else 0
                
                # Рассчитываем метрики предыдущего года
                prev_interests = len(prev_year_interests)
                prev_unique_interests = get_unique_interests(prev_year_interests)
                prev_deals = len(prev_year_deals)
                prev_conversion = (prev_deals / prev_unique_interests * 100) if prev_unique_interests > 0 else 0
                
                # Рассчитываем дельты
                def calculate_delta(current, previous):
                    if previous == 0:
                        return 0
                    return ((current - previous) / previous) * 100
                
                delta_interests = calculate_delta(current_interests, prev_interests)
                delta_unique = calculate_delta(current_unique_interests, prev_unique_interests)
                delta_deals = calculate_delta(current_deals, prev_deals)
                delta_conversion = calculate_delta(current_conversion, prev_conversion)
                
                return {
                    'interests': {'current': current_interests, 'delta': delta_interests},
                    'unique': {'current': current_unique_interests, 'delta': delta_unique},
                    'deals': {'current': current_deals, 'delta': delta_deals},
                    'conversion': {'current': current_conversion, 'delta': delta_conversion}
                }
            
            # Рассчитываем метрики текущего года
            current_year_metrics = calculate_current_year_metrics(interests_df, deals_df)
            
            # Создаем график сравнения уникальных интересов по месяцам
            def create_comparison_chart(interests_df):
                # Фильтруем данные за 2024 и 2025 годы
                interests_2024 = interests_df[interests_df['Дата создания'].dt.year == 2024].copy()
                interests_2025 = interests_df[interests_df['Дата создания'].dt.year == 2025].copy()
                
                # Добавляем месяц для группировки
                interests_2024['Месяц'] = interests_2024['Дата создания'].dt.month
                interests_2025['Месяц'] = interests_2025['Дата создания'].dt.month
                
                # Подсчитываем уникальные интересы по месяцам для каждого года
                monthly_data_2024 = []
                monthly_data_2025 = []
                months_2025 = []
                
                # Для 2024 года - все 12 месяцев
                for month in range(1, 13):
                    month_data_2024 = interests_2024[interests_2024['Месяц'] == month]
                    unique_2024 = get_unique_interests(month_data_2024)
                    monthly_data_2024.append(unique_2024)
                
                # Для 2025 года - только месяцы с данными
                months_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
                max_month_2025 = interests_2025['Месяц'].max() if len(interests_2025) > 0 else 0
                
                for month in range(1, max_month_2025 + 1):
                    month_data_2025 = interests_2025[interests_2025['Месяц'] == month]
                    unique_2025 = get_unique_interests(month_data_2025)
                    monthly_data_2025.append(unique_2025)
                    months_2025.append(months_names[month - 1])
                
                # Создаем график
                months_2024 = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
                
                fig = go.Figure()
                
                # Линия для 2024 года
                fig.add_trace(go.Scatter(
                    x=months_2024,
                    y=monthly_data_2024,
                    mode='lines+markers+text',
                    name='2024 год',
                    line=dict(color='#86a7c8', width=3, shape='spline'),
                    marker=dict(size=8, color='#86a7c8'),
                    text=monthly_data_2024,
                    textposition='top center',
                    textfont=dict(size=11, color='#2c3e50'),
                    hovertemplate='<b>%{x} 2024</b><br>Уникальные интересы: %{y}<extra></extra>'
                ))
                
                # Линия для 2025 года (только если есть данные)
                if len(monthly_data_2025) > 0:
                    fig.add_trace(go.Scatter(
                        x=months_2025,
                        y=monthly_data_2025,
                        mode='lines+markers+text',
                        name='2025 год',
                        line=dict(color='#eea591', width=3, shape='spline'),
                        marker=dict(size=8, color='#eea591'),
                        text=monthly_data_2025,
                        textposition='bottom center',
                        textfont=dict(size=11, color='#2c3e50'),
                        hovertemplate='<b>%{x} 2025</b><br>Уникальные интересы: %{y}<extra></extra>'
                    ))
                
                # Настройка макета
                fig.update_layout(
                    title={
                        'text': '📈 Сравнение уникальных интересов по месяцам (2024 vs 2025)',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12, color='#2c3e50'),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=80, b=50),
                    hovermode='x unified'
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                return fig
            
            # Создаем график сравнения сделок по месяцам
            def create_deals_comparison_chart(deals_df):
                # Фильтруем данные за 2024 и 2025 годы
                deals_2024 = deals_df[deals_df['Дата_из_ссылки'].dt.year == 2024].copy()
                deals_2025 = deals_df[deals_df['Дата_из_ссылки'].dt.year == 2025].copy()
                
                # Добавляем месяц для группировки
                deals_2024['Месяц'] = deals_2024['Дата_из_ссылки'].dt.month
                deals_2025['Месяц'] = deals_2025['Дата_из_ссылки'].dt.month
                
                # Подсчитываем сделки по месяцам для каждого года
                monthly_deals_2024 = []
                monthly_deals_2025 = []
                months_2025 = []
                
                # Для 2024 года - все 12 месяцев
                for month in range(1, 13):
                    month_data_2024 = deals_2024[deals_2024['Месяц'] == month]
                    deals_count_2024 = len(month_data_2024)
                    monthly_deals_2024.append(deals_count_2024)
                
                # Для 2025 года - только месяцы с данными
                months_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
                max_month_2025 = deals_2025['Месяц'].max() if len(deals_2025) > 0 else 0
                
                for month in range(1, max_month_2025 + 1):
                    month_data_2025 = deals_2025[deals_2025['Месяц'] == month]
                    deals_count_2025 = len(month_data_2025)
                    monthly_deals_2025.append(deals_count_2025)
                    months_2025.append(months_names[month - 1])
                
                # Создаем график
                months_2024 = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
                
                fig = go.Figure()
                
                # Столбцы для 2024 года
                fig.add_trace(go.Bar(
                    x=months_2024,
                    y=monthly_deals_2024,
                    name='2024 год',
                    marker_color='#86a7c8',
                    text=monthly_deals_2024,
                    textposition='outside',
                    textfont=dict(size=11, color='#2c3e50'),
                    hovertemplate='<b>%{x} 2024</b><br>Количество сделок: %{y}<extra></extra>'
                ))
                
                # Столбцы для 2025 года (только если есть данные)
                if len(monthly_deals_2025) > 0:
                    fig.add_trace(go.Bar(
                        x=months_2025,
                        y=monthly_deals_2025,
                        name='2025 год',
                        marker_color='#eea591',
                        text=monthly_deals_2025,
                        textposition='outside',
                        textfont=dict(size=11, color='#2c3e50'),
                        hovertemplate='<b>%{x} 2025</b><br>Количество сделок: %{y}<extra></extra>'
                    ))
                
                # Настройка макета
                fig.update_layout(
                    title={
                        'text': '📊 Сравнение сделок по месяцам (2024 vs 2025)',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12, color='#2c3e50'),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=80, b=50),
                    hovermode='x unified',
                    barmode='group'  # Группированные столбцы
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                return fig
            
            # Создаем карточки с дельтой
            current_cards = [
                {
                    "label": "Интересы (2025)",
                    "value": str(current_year_metrics['interests']['current']),
                    "delta": f"{current_year_metrics['interests']['delta']:+.1f}%",
                    "metric": "interests",
                    "caption": "Сравнение с 2024 годом"
                },
                {
                    "label": "Уникальные интересы (2025)",
                    "value": str(current_year_metrics['unique']['current']),
                    "delta": f"{current_year_metrics['unique']['delta']:+.1f}%",
                    "metric": "unique",
                    "caption": "Сравнение с 2024 годом"
                },
                {
                    "label": "Сделки (2025)",
                    "value": str(current_year_metrics['deals']['current']),
                    "delta": f"{current_year_metrics['deals']['delta']:+.1f}%",
                    "metric": "deals",
                    "caption": "Сравнение с 2024 годом"
                },
                {
                    "label": "Конверсия (2025)",
                    "value": f"{current_year_metrics['conversion']['current']:.1f}%",
                    "delta": f"{current_year_metrics['conversion']['delta']:+.1f}%",
                    "metric": "conversion",
                    "caption": "Сравнение с 2024 годом"
                },
            ]
            
            cols = st.columns(4)
            for card, col in zip(current_cards, cols):
                with col:
                    # Определяем цвет для дельты
                    delta_color = "#3b82f6" if current_year_metrics[card['metric']]['delta'] >= 0 else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="kpi-card-delta">
                        <div class="kpi-label">{card['label']}</div>
                        <div class="kpi-value">{card['value']}</div>
                        <div style="color: {delta_color} !important; font-size: 1rem; margin-bottom: 3px; font-weight: 500; display: block;">{card['delta']}</div>
                        <div class="kpi-caption">{card['caption']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Создаем графики сравнения
            comparison_chart = create_comparison_chart(interests_df)
            deals_comparison_chart = create_deals_comparison_chart(deals_df)
            
            # Показываем графики сравнения рядом
            if comparison_chart and deals_comparison_chart:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.plotly_chart(comparison_chart, use_container_width=True, key="comparison_chart")
                with col2:
                    st.plotly_chart(deals_comparison_chart, use_container_width=True, key="deals_comparison_chart")
            
            # Создаем графики для текущего года (2025)
            def create_current_year_interest_types_chart(interests_df):
                # Фильтруем данные только за 2025 год
                current_year_interests = interests_df[interests_df['Дата создания'].dt.year == 2025]
                
                if len(current_year_interests) == 0:
                    return None
                
                # Подсчитываем уникальные интересы по видам событий
                event_unique_interests = {}
                
                for event_type in current_year_interests['Вид события_классифицированный'].unique():
                    event_data = current_year_interests[current_year_interests['Вид события_классифицированный'] == event_type]
                    unique_count = get_unique_interests(event_data)
                    event_unique_interests[event_type] = unique_count
                
                # Сортируем по количеству уникальных интересов
                event_counts = pd.Series(event_unique_interests)
                
                # Цвета для разных видов событий
                colors = {
                    'Сайт': '#86a7c8',
                    'Телефонный звонок': '#eea591', 
                    'Электронное письмо': '#5a7ca6',
                    'Прочее': '#466494'
                }
                
                # Создаем круговую диаграмму (donut chart)
                fig = go.Figure()
                
                fig.add_trace(go.Pie(
                    labels=event_counts.index,
                    values=event_counts.values,
                    hole=0.6,  # Делаем отверстие в центре для donut chart
                    marker_colors=[colors.get(event_type, '#cccccc') for event_type in event_counts.index],
                    textinfo='label+percent+value',
                    textposition='outside',
                    textfont=dict(size=12, color='#2c3e50'),
                    hovertemplate='<b>%{label}</b><br>Количество: %{value}<br>Процент: %{percent}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': '📊 Распределение видов интересов (2025)',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 16, 'color': '#2c3e50'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12, color='#2c3e50'),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=20, r=150, t=60, b=20),
                    showlegend=True
                )
                
                # Добавляем центральный текст с общим количеством
                total_count = event_counts.sum()
                fig.add_annotation(
                    text=f"<b>{total_count}</b><br>Интересов",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=14, color='#2c3e50'),
                    align="center"
                )
                
                return fig
            
            def create_current_year_interest_source_chart(interests_df):
                # Фильтруем данные только за 2025 год
                current_year_interests = interests_df[interests_df['Дата создания'].dt.year == 2025]
                
                if len(current_year_interests) == 0:
                    return None
                
                # Подсчитываем количество по источникам интереса
                source_counts = current_year_interests['Источник интереса'].value_counts()
                
                # Объединяем похожие источники
                combined_sources = {}
                
                for source, count in source_counts.items():
                    # Объединяем прямые заходы
                    if source in ['Прямой заход', 'Прямые заходы', '<>']:
                        combined_sources['Прямые заходы'] = combined_sources.get('Прямые заходы', 0) + count
                    else:
                        combined_sources[source] = count
                
                # Сортируем от большего к меньшему
                sorted_sources = dict(sorted(combined_sources.items(), key=lambda x: x[1], reverse=True))
                
                # Берем топ-10 источников для лучшей читаемости
                top_sources = dict(list(sorted_sources.items())[:10])
                
                # Яркие цвета для источников (заменяем темные на яркие)
                colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                         '#1abc9c', '#e67e22', '#34495e', '#16a085', '#8e44ad']
                
                # Создаем горизонтальную столбчатую диаграмму
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=list(top_sources.keys()),
                    x=list(top_sources.values()),
                    orientation='h',
                    marker_color=colors[:len(top_sources)],
                    text=list(top_sources.values()),
                    textposition='auto',
                    textfont=dict(size=12, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>%{y}</b><br>Количество: %{x}<extra></extra>'
                ))
                
                # Настройка макета
                fig.update_layout(
                    title={
                        'text': '📊 Источники интересов (2025)',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="Количество",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    showlegend=False
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                fig.update_yaxes(
                    showgrid=False,
                    zeroline=False
                )
                
                return fig
            
            # Создаем графики для текущего года
            current_year_interest_types_chart = create_current_year_interest_types_chart(interests_df)
            current_year_interest_source_chart = create_current_year_interest_source_chart(interests_df)
            
            # Показываем графики в трех колонках
            if current_year_interest_types_chart and current_year_interest_source_chart:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.plotly_chart(current_year_interest_types_chart, use_container_width=True, key="interest_types_current_year")
                with col2:
                    st.plotly_chart(current_year_interest_source_chart, use_container_width=True, key="interest_source_current_year")
                with col3:
                    # Создаем график уникальных интересов по проекту за 2025
                    def create_current_year_project_interests_chart(interests_df):
                        # Фильтруем данные только за 2025 год
                        current_year_interests = interests_df[interests_df['Дата создания'].dt.year == 2025]
                        
                        if len(current_year_interests) == 0:
                            return None
                        
                        # Подсчитываем уникальные интересы по проектам
                        project_unique_interests = {}
                        
                        # Получаем все уникальные проекты, включая NaN
                        all_projects = current_year_interests['Проект_обработанный'].dropna().unique()
                        all_projects = list(all_projects) + ['Пустой']  # Добавляем "Пустой" явно
                        
                        for project in all_projects:
                            if project == 'Пустой':
                                # Для пустых проектов берем записи с NaN в исходной колонке
                                project_data = current_year_interests[current_year_interests['Проект'].isna()]
                            else:
                                project_data = current_year_interests[current_year_interests['Проект_обработанный'] == project]
                            
                            if len(project_data) > 0:
                                unique_count = get_unique_interests(project_data)
                                project_unique_interests[project] = unique_count
                        
                        # Сортируем по количеству уникальных интересов
                        sorted_projects = dict(sorted(project_unique_interests.items(), key=lambda x: x[1], reverse=True))
                        
                        # Цвета для проектов
                        colors = {
                            'Кровля и Фасады': '#3498db',
                            'Ангары': '#e74c3c',
                            'Блоки': '#2ecc71',
                            'Дома': '#f39c12',
                            'Снабжение': '#9b59b6',
                            'Фасады': '#1abc9c',
                            'Пустой': '#95a5a6'
                        }
                        
                        # Создаем круговую диаграмму (donut chart)
                        fig = go.Figure()
                        
                        fig.add_trace(go.Pie(
                            labels=list(sorted_projects.keys()),
                            values=list(sorted_projects.values()),
                            hole=0,  # Убираем отверстие - обычная круговая диаграмма
                            marker_colors=[colors.get(project, '#cccccc') for project in sorted_projects.keys()],
                            textinfo='label+percent+value',
                            textposition='outside',
                            textfont=dict(size=12, color='#2c3e50'),
                            hovertemplate='<b>%{label}</b><br>Уникальные интересы: %{value}<br>Процент: %{percent}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title={
                                'text': '📊 Уникальные интересы по проекту (2025)',
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': {'size': 16, 'color': '#2c3e50'}
                            },
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(family="Arial", size=12, color='#2c3e50'),
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                bgcolor='rgba(255,255,255,0.8)',
                                bordercolor='lightgray',
                                borderwidth=1
                            ),
                            margin=dict(l=20, r=150, t=60, b=20),
                            showlegend=True
                        )
                        
                        # Убираем центральный текст
                        
                        return fig
                    
                    # Создаем и показываем график
                    current_year_project_chart = create_current_year_project_interests_chart(interests_df)
                    if current_year_project_chart:
                        st.plotly_chart(current_year_project_chart, use_container_width=True, key="project_interests_current_year")
                    else:
                        st.markdown("### 📈 Уникальные интересы по проекту")
                        st.markdown("*Нет данных для 2025 года*")
            
            # Разделительная линия
            st.markdown("---")
            
            # Блок "Текущий месяц"
            st.subheader("📅 Анализ текущего месяца")
            
            # Создаем карточки с дельтой для текущего месяца
            def calculate_current_month_metrics(interests_df, deals_df):
                # Находим текущий месяц и год
                current_date = datetime.now()
                current_month = current_date.month
                current_year = current_date.year
                current_day = current_date.day
                
                # Находим последнюю дату с данными в текущем месяце
                current_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == current_year) & 
                    (interests_df['Дата создания'].dt.month == current_month)
                ]
                
                current_month_deals = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == current_year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_month)
                ]
                
                # Находим последний день с данными в текущем месяце
                if len(current_month_interests) > 0:
                    last_day_with_data = current_month_interests['Дата создания'].dt.day.max()
                elif len(current_month_deals) > 0:
                    last_day_with_data = current_month_deals['Дата_из_ссылки'].dt.day.max()
                else:
                    last_day_with_data = current_day
                
                # Используем минимальное значение между текущим днем и последним днем с данными
                end_day = min(current_day, last_day_with_data)
                
                # Фильтруем данные за текущий месяц до последней даты с данными
                current_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == current_year) & 
                    (interests_df['Дата создания'].dt.month == current_month) &
                    (interests_df['Дата создания'].dt.day <= end_day)
                ]
                
                current_month_deals = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == current_year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_month) &
                    (deals_df['Дата_из_ссылки'].dt.day <= end_day)
                ]
                
                # Фильтруем данные за тот же период прошлого года
                prev_year = current_year - 1
                
                prev_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == prev_year) & 
                    (interests_df['Дата создания'].dt.month == current_month) &
                    (interests_df['Дата создания'].dt.day <= end_day)
                ]
                
                prev_month_deals = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == prev_year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_month) &
                    (deals_df['Дата_из_ссылки'].dt.day <= end_day)
                ]
                
                # Рассчитываем метрики
                current_interests = len(current_month_interests)
                current_unique = get_unique_interests(current_month_interests)
                current_deals = len(current_month_deals)
                current_conversion = (current_deals / current_unique * 100) if current_unique > 0 else 0
                
                prev_interests = len(prev_month_interests)
                prev_unique = get_unique_interests(prev_month_interests)
                prev_deals = len(prev_month_deals)
                prev_conversion = (prev_deals / prev_unique * 100) if prev_unique > 0 else 0
                
                # Рассчитываем дельты
                def calculate_delta(current, previous):
                    if previous == 0:
                        return 100 if current > 0 else 0
                    return ((current - previous) / previous) * 100
                
                return {
                    'interests': {
                        'current': current_interests,
                        'previous': prev_interests,
                        'delta': calculate_delta(current_interests, prev_interests)
                    },
                    'unique': {
                        'current': current_unique,
                        'previous': prev_unique,
                        'delta': calculate_delta(current_unique, prev_unique)
                    },
                    'deals': {
                        'current': current_deals,
                        'previous': prev_deals,
                        'delta': calculate_delta(current_deals, prev_deals)
                    },
                    'conversion': {
                        'current': current_conversion,
                        'previous': prev_conversion,
                        'delta': calculate_delta(current_conversion, prev_conversion)
                    }
                }
            
            # Создаем карточки с дельтой для текущего месяца
            current_month_metrics = calculate_current_month_metrics(interests_df, deals_df)
            
            current_month_cards = [
                {
                    "label": "Интересы (текущий месяц)",
                    "value": str(current_month_metrics['interests']['current']),
                    "delta": f"{current_month_metrics['interests']['delta']:+.1f}%",
                    "metric": "interests",
                    "caption": "Сравнение с тем же периодом прошлого года"
                },
                {
                    "label": "Уникальные интересы (текущий месяц)",
                    "value": str(current_month_metrics['unique']['current']),
                    "delta": f"{current_month_metrics['unique']['delta']:+.1f}%",
                    "metric": "unique",
                    "caption": "Сравнение с тем же периодом прошлого года"
                },
                {
                    "label": "Сделки (текущий месяц)",
                    "value": str(current_month_metrics['deals']['current']),
                    "delta": f"{current_month_metrics['deals']['delta']:+.1f}%",
                    "metric": "deals",
                    "caption": "Сравнение с тем же периодом прошлого года"
                },
                {
                    "label": "Конверсия (текущий месяц)",
                    "value": f"{current_month_metrics['conversion']['current']:.1f}%",
                    "delta": f"{current_month_metrics['conversion']['delta']:+.1f}%",
                    "metric": "conversion",
                    "caption": "Сравнение с тем же периодом прошлого года"
                },
            ]
            
            cols = st.columns(4)
            for card, col in zip(current_month_cards, cols):
                with col:
                    # Определяем цвет для дельты
                    delta_color = "#3b82f6" if current_month_metrics[card['metric']]['delta'] >= 0 else "#ef4444"
                    
                    st.markdown(f"""
                    <div class="kpi-card-delta">
                        <div class="kpi-label">{card['label']}</div>
                        <div class="kpi-value">{card['value']}</div>
                        <div style="color: {delta_color} !important; font-size: 1rem; margin-bottom: 3px; font-weight: 500; display: block;">{card['delta']}</div>
                        <div class="kpi-caption">{card['caption']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Создаем графики для текущего месяца
            def create_current_month_interest_types_chart(interests_df):
                # Фильтруем данные только за текущий месяц
                current_date = datetime.now()
                current_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == current_date.year) & 
                    (interests_df['Дата создания'].dt.month == current_date.month)
                ]
                
                if len(current_month_interests) == 0:
                    return None
                
                # Подсчитываем уникальные интересы по видам событий
                event_unique_interests = {}
                
                for event_type in current_month_interests['Вид события_классифицированный'].unique():
                    event_data = current_month_interests[current_month_interests['Вид события_классифицированный'] == event_type]
                    unique_count = get_unique_interests(event_data)
                    event_unique_interests[event_type] = unique_count
                
                # Сортируем по количеству уникальных интересов
                event_counts = pd.Series(event_unique_interests)
                
                # Цвета для разных видов событий
                colors = {
                    'Сайт': '#86a7c8',
                    'Телефонный звонок': '#eea591', 
                    'Электронное письмо': '#5a7ca6',
                    'Прочее': '#466494'
                }
                
                # Создаем круговую диаграмму (donut chart)
                fig = go.Figure()
                
                fig.add_trace(go.Pie(
                    labels=event_counts.index,
                    values=event_counts.values,
                    hole=0.6,  # Делаем отверстие в центре для donut chart
                    marker_colors=[colors.get(event_type, '#cccccc') for event_type in event_counts.index],
                    textinfo='label+percent+value',
                    textposition='outside',
                    textfont=dict(size=12, color='#2c3e50'),
                    hovertemplate='<b>%{label}</b><br>Количество: %{value}<br>Процент: %{percent}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': f'📊 Распределение видов интересов ({current_date.strftime("%B %Y")})',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 16, 'color': '#2c3e50'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12, color='#2c3e50'),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=20, r=150, t=60, b=20),
                    showlegend=True
                )
                
                # Добавляем центральный текст с общим количеством
                total_count = event_counts.sum()
                fig.add_annotation(
                    text=f"<b>{total_count}</b><br>Интересов",
                    x=0.5, y=0.5,
                    xref="paper", yref="paper",
                    showarrow=False,
                    font=dict(size=14, color='#2c3e50'),
                    align="center"
                )
                
                return fig
            
            def create_current_month_interest_source_chart(interests_df):
                # Фильтруем данные только за текущий месяц
                current_date = datetime.now()
                current_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == current_date.year) & 
                    (interests_df['Дата создания'].dt.month == current_date.month)
                ]
                
                if len(current_month_interests) == 0:
                    return None
                
                # Подсчитываем количество по источникам интереса
                source_counts = current_month_interests['Источник интереса'].value_counts()
                
                # Объединяем похожие источники
                combined_sources = {}
                
                for source, count in source_counts.items():
                    # Объединяем прямые заходы
                    if source in ['Прямой заход', 'Прямые заходы', '<>']:
                        combined_sources['Прямые заходы'] = combined_sources.get('Прямые заходы', 0) + count
                    else:
                        combined_sources[source] = count
                
                # Сортируем от большего к меньшему
                sorted_sources = dict(sorted(combined_sources.items(), key=lambda x: x[1], reverse=True))
                
                # Берем топ-10 источников для лучшей читаемости
                top_sources = dict(list(sorted_sources.items())[:10])
                
                # Яркие цвета для источников (заменяем темные на яркие)
                colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                         '#1abc9c', '#e67e22', '#34495e', '#16a085', '#8e44ad']
                
                # Создаем горизонтальную столбчатую диаграмму
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=list(top_sources.keys()),
                    x=list(top_sources.values()),
                    orientation='h',
                    marker_color=colors[:len(top_sources)],
                    text=list(top_sources.values()),
                    textposition='auto',
                    textfont=dict(size=12, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>%{y}</b><br>Количество: %{x}<extra></extra>'
                ))
                
                # Настройка макета
                fig.update_layout(
                    title={
                        'text': f'📊 Источники интересов ({current_date.strftime("%B %Y")})',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="Количество",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12),
                    margin=dict(l=50, r=50, t=80, b=50),
                    showlegend=False
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                fig.update_yaxes(
                    showgrid=False,
                    zeroline=False
                )
                
                return fig
            
            # Создаем графики для текущего месяца
            current_month_interest_types_chart = create_current_month_interest_types_chart(interests_df)
            current_month_interest_source_chart = create_current_month_interest_source_chart(interests_df)
            
            # Создаем графики сравнения для текущего месяца
            def create_current_month_comparison_chart(interests_df):
                # Получаем текущий месяц и год
                current_date = datetime.now()
                current_month = current_date.month
                current_year = current_date.year
                prev_year = current_year - 1
                
                # Получаем текущий день месяца
                current_day = current_date.day
                
                # Создаем временную шкалу для полного месяца (1-31)
                days = list(range(1, 32))
                
                # Данные за текущий месяц текущего года
                current_month_data = interests_df[
                    (interests_df['Дата создания'].dt.year == current_year) & 
                    (interests_df['Дата создания'].dt.month == current_month)
                ]
                
                # Данные за текущий месяц прошлого года
                prev_month_data = interests_df[
                    (interests_df['Дата создания'].dt.year == prev_year) & 
                    (interests_df['Дата создания'].dt.month == current_month)
                ]
                
                # Подсчитываем уникальные интересы по дням
                current_daily_interests = []
                prev_daily_interests = []
                valid_days = []
                
                for day in days:
                    # Текущий год - показываем только до текущего дня
                    if day <= current_day:
                        day_data_current = current_month_data[
                            current_month_data['Дата создания'].dt.day == day
                        ]
                        current_count = get_unique_interests(day_data_current)
                    else:
                        current_count = 0
                    
                    # Прошлый год - показываем за весь месяц
                    day_data_prev = prev_month_data[
                        prev_month_data['Дата создания'].dt.day == day
                    ]
                    prev_count = get_unique_interests(day_data_prev)
                    
                    # Добавляем день если есть данные в прошлом году или в текущем году (до текущего дня)
                    if prev_count > 0 or (day <= current_day and current_count > 0):
                        current_daily_interests.append(current_count)
                        prev_daily_interests.append(prev_count)
                        valid_days.append(day)
                
                # Создаем график
                fig = go.Figure()
                
                # Линия текущего года
                fig.add_trace(go.Scatter(
                    x=valid_days,
                    y=current_daily_interests,
                    mode='lines+markers+text',
                    name=f'Уникальные интересы ({current_year})',
                    line=dict(color='#3498db', width=4, shape='spline'),
                    marker=dict(size=8, color='#3498db', line=dict(width=2, color='white')),
                    text=current_daily_interests,
                    textposition='top center',
                    textfont=dict(size=10, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>День %{x}</b><br>Уникальные интересы: %{y}<extra></extra>'
                ))
                
                # Линия прошлого года
                fig.add_trace(go.Scatter(
                    x=valid_days,
                    y=prev_daily_interests,
                    mode='lines+markers+text',
                    name=f'Уникальные интересы ({prev_year})',
                    line=dict(color='#e74c3c', width=3, shape='spline'),
                    marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='white')),
                    text=prev_daily_interests,
                    textposition='bottom center',
                    textfont=dict(size=10, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>День %{x}</b><br>Уникальные интересы: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': f'📈 Сравнение уникальных интересов по дням ({current_date.strftime("%B")})',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="День месяца",
                    yaxis_title="Уникальные интересы",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=80, b=50),
                    hovermode='x unified'
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False,
                    range=[0.5, 31.5]
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                return fig
            
            def create_current_month_deals_comparison_chart(deals_df):
                # Получаем текущий месяц и год
                current_date = datetime.now()
                current_month = current_date.month
                current_year = current_date.year
                prev_year = current_year - 1
                
                # Создаем временную шкалу 1-31 день
                days = list(range(1, 32))
                
                # Данные за текущий месяц текущего года
                current_month_data = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == current_year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_month)
                ]
                
                # Данные за текущий месяц прошлого года
                prev_month_data = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == prev_year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_month)
                ]
                
                # Получаем текущий день месяца
                current_day = current_date.day
                
                # Подсчитываем сделки по дням
                current_daily_deals = []
                prev_daily_deals = []
                valid_days = []
                
                for day in days:
                    # Текущий год - показываем только до текущего дня
                    if day <= current_day:
                        day_data_current = current_month_data[
                            current_month_data['Дата_из_ссылки'].dt.day == day
                        ]
                        current_count = len(day_data_current)
                    else:
                        current_count = 0
                    
                    # Прошлый год - показываем за весь месяц
                    day_data_prev = prev_month_data[
                        prev_month_data['Дата_из_ссылки'].dt.day == day
                    ]
                    prev_count = len(day_data_prev)
                    
                    # Добавляем день если есть данные в прошлом году или в текущем году (до текущего дня)
                    if prev_count > 0 or (day <= current_day and current_count > 0):
                        current_daily_deals.append(current_count)
                        prev_daily_deals.append(prev_count)
                        valid_days.append(day)
                
                # Создаем график
                fig = go.Figure()
                
                # Линия текущего года
                fig.add_trace(go.Scatter(
                    x=valid_days,
                    y=current_daily_deals,
                    mode='lines+markers+text',
                    name=f'Сделки ({current_year})',
                    line=dict(color='#2ecc71', width=4, shape='spline'),
                    marker=dict(size=8, color='#2ecc71', line=dict(width=2, color='white')),
                    text=current_daily_deals,
                    textposition='top center',
                    textfont=dict(size=10, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>День %{x}</b><br>Сделки: %{y}<extra></extra>'
                ))
                
                # Линия прошлого года
                fig.add_trace(go.Scatter(
                    x=valid_days,
                    y=prev_daily_deals,
                    mode='lines+markers+text',
                    name=f'Сделки ({prev_year})',
                    line=dict(color='#f39c12', width=3, shape='spline'),
                    marker=dict(size=8, color='#f39c12', line=dict(width=2, color='white')),
                    text=prev_daily_deals,
                    textposition='bottom center',
                    textfont=dict(size=10, color='#2c3e50', weight='bold'),
                    hovertemplate='<b>День %{x}</b><br>Сделки: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': f'📈 Сравнение сделок по дням ({current_date.strftime("%B")})',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="День месяца",
                    yaxis_title="Количество сделок",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=80, b=50),
                    hovermode='x unified'
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False,
                    range=[0.5, 31.5]
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                return fig
            
            # Создаем графики сравнения для текущего месяца
            current_month_comparison_chart = create_current_month_comparison_chart(interests_df)
            current_month_deals_comparison_chart = create_current_month_deals_comparison_chart(deals_df)
            
            # Показываем графики сравнения рядом
            if current_month_comparison_chart and current_month_deals_comparison_chart:
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.plotly_chart(current_month_comparison_chart, use_container_width=True, key="comparison_current_month")
                with col2:
                    st.plotly_chart(current_month_deals_comparison_chart, use_container_width=True, key="deals_comparison_current_month")
            
            # Показываем графики в трех колонках
            if current_month_interest_types_chart and current_month_interest_source_chart:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.plotly_chart(current_month_interest_types_chart, use_container_width=True, key="interest_types_current_month")
                with col2:
                    st.plotly_chart(current_month_interest_source_chart, use_container_width=True, key="interest_source_current_month")
                with col3:
                    # Создаем график уникальных интересов по проекту за текущий месяц
                    def create_current_month_project_interests_chart(interests_df):
                        # Фильтруем данные только за текущий месяц
                        current_date = datetime.now()
                        current_month_interests = interests_df[
                            (interests_df['Дата создания'].dt.year == current_date.year) & 
                            (interests_df['Дата создания'].dt.month == current_date.month)
                        ]
                        
                        if len(current_month_interests) == 0:
                            return None
                        
                        # Подсчитываем уникальные интересы по проектам
                        project_unique_interests = {}
                        
                        # Получаем все уникальные проекты, включая NaN
                        all_projects = current_month_interests['Проект_обработанный'].dropna().unique()
                        all_projects = list(all_projects) + ['Пустой']  # Добавляем "Пустой" явно
                        
                        for project in all_projects:
                            if project == 'Пустой':
                                # Для пустых проектов берем записи с NaN в исходной колонке
                                project_data = current_month_interests[current_month_interests['Проект'].isna()]
                            else:
                                project_data = current_month_interests[current_month_interests['Проект_обработанный'] == project]
                            
                            if len(project_data) > 0:
                                unique_count = get_unique_interests(project_data)
                                project_unique_interests[project] = unique_count
                        
                        # Сортируем по количеству уникальных интересов
                        sorted_projects = dict(sorted(project_unique_interests.items(), key=lambda x: x[1], reverse=True))
                        
                        # Цвета для проектов
                        colors = {
                            'Кровля и Фасады': '#3498db',
                            'Ангары': '#e74c3c',
                            'Блоки': '#2ecc71',
                            'Дома': '#f39c12',
                            'Снабжение': '#9b59b6',
                            'Фасады': '#1abc9c',
                            'Пустой': '#95a5a6'
                        }
                        
                        # Создаем круговую диаграмму (donut chart)
                        fig = go.Figure()
                        
                        fig.add_trace(go.Pie(
                            labels=list(sorted_projects.keys()),
                            values=list(sorted_projects.values()),
                            hole=0,  # Убираем отверстие - обычная круговая диаграмма
                            marker_colors=[colors.get(project, '#cccccc') for project in sorted_projects.keys()],
                            textinfo='label+percent+value',
                            textposition='outside',
                            textfont=dict(size=12, color='#2c3e50'),
                            hovertemplate='<b>%{label}</b><br>Уникальные интересы: %{value}<br>Процент: %{percent}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title={
                                'text': f'📊 Уникальные интересы по проекту ({current_date.strftime("%B %Y")})',
                                'x': 0.5,
                                'xanchor': 'center',
                                'font': {'size': 16, 'color': '#2c3e50'}
                            },
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(family="Arial", size=12, color='#2c3e50'),
                            legend=dict(
                                orientation="v",
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.02,
                                bgcolor='rgba(255,255,255,0.8)',
                                bordercolor='lightgray',
                                borderwidth=1
                            ),
                            margin=dict(l=20, r=150, t=60, b=20),
                            showlegend=True
                        )
                        
                        # Убираем центральный текст
                        
                        return fig
                    
                    # Создаем и показываем график
                    current_month_project_chart = create_current_month_project_interests_chart(interests_df)
                    if current_month_project_chart:
                        st.plotly_chart(current_month_project_chart, use_container_width=True, key="project_interests_current_month")
                    else:
                        st.markdown("### 📈 Уникальные интересы по проекту")
                        st.markdown("*Нет данных для текущего месяца*")
            
            # Добавляем график по менеджерам
            def create_current_month_manager_chart(interests_df, deals_df):
                # Фильтруем данные только за текущий месяц
                current_date = datetime.now()
                current_month_interests = interests_df[
                    (interests_df['Дата создания'].dt.year == current_date.year) & 
                    (interests_df['Дата создания'].dt.month == current_date.month)
                ]
                
                current_month_deals = deals_df[
                    (deals_df['Дата_из_ссылки'].dt.year == current_date.year) & 
                    (deals_df['Дата_из_ссылки'].dt.month == current_date.month)
                ]
                
                if len(current_month_interests) == 0 and len(current_month_deals) == 0:
                    return None
                
                # Подсчитываем интересы и сделки по ответственным
                manager_data = {}
                
                # Обрабатываем интересы
                for _, row in current_month_interests.iterrows():
                    manager = row.get('Ответственный', 'Не указан')
                    if manager not in manager_data:
                        manager_data[manager] = {'interests': 0, 'deals': 0}
                    manager_data[manager]['interests'] += 1
                
                # Обрабатываем сделки
                for _, row in current_month_deals.iterrows():
                    manager = row.get('Ответственный', 'Не указан')
                    if manager not in manager_data:
                        manager_data[manager] = {'interests': 0, 'deals': 0}
                    manager_data[manager]['deals'] += 1
                
                if not manager_data:
                    return None
                
                # Исключаем менеджеров 'Матренина' и 'Сокрутенко'
                manager_data = {k: v for k, v in manager_data.items() if 'Матренина' not in str(k) and 'Сокрутенко' not in str(k)}
                
                # Сортируем менеджеров по интересам и сделкам (убывание)
                sorted_managers = sorted(manager_data.items(), key=lambda x: (-x[1]['interests'], -x[1]['deals']))
                managers = [m[0] for m in sorted_managers]
                interests_counts = [m[1]['interests'] for m in sorted_managers]
                deals_counts = [m[1]['deals'] for m in sorted_managers]
                
                # Создаем график с двумя столбцами
                fig = go.Figure()
                
                # Столбцы для интересов
                fig.add_trace(go.Bar(
                    x=managers,
                    y=interests_counts,
                    name='Интересы',
                    marker_color='#3498db',
                    text=interests_counts,
                    textposition='auto',
                    textfont=dict(size=12, color='white', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Интересы: %{y}<extra></extra>'
                ))
                
                # Столбцы для сделок
                fig.add_trace(go.Bar(
                    x=managers,
                    y=deals_counts,
                    name='Сделки',
                    marker_color='#e74c3c',
                    text=deals_counts,
                    textposition='auto',
                    textfont=dict(size=12, color='white', weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Сделки: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': f'👥 Менеджеры: интересы и сделки ({current_date.strftime("%B %Y")})',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#2c3e50'}
                    },
                    xaxis_title="Менеджер",
                    yaxis_title="Количество",
                    height=500,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial", size=12),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.8)',
                        bordercolor='lightgray',
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=80, b=50),
                    barmode='group'  # Группируем столбцы
                )
                
                # Настройка осей
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=False
                )
                
                fig.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray',
                    zeroline=True,
                    zerolinecolor='lightgray'
                )
                
                return fig
            
            # Создаем и показываем график по менеджерам
            current_month_manager_chart = create_current_month_manager_chart(interests_df, deals_df)
            if current_month_manager_chart:
                st.plotly_chart(current_month_manager_chart, use_container_width=True, key="manager_chart_current_month")
            else:
                st.markdown("### 👥 Менеджеры: интересы и сделки")
                st.markdown("*Нет данных для текущего месяца*")
    
    else:
        st.error("❌ Не удалось загрузить данные. Проверьте наличие файлов Excel.")

if __name__ == "__main__":
    main() 