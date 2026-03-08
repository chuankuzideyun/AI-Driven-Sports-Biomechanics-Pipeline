import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from processor import SprintDataProcessor
from main import AthleraAnalyzer

# --- Unit Tests for Processor ---

@pytest.fixture
def sample_sprint_df():
    """Create a simulated sports data DataFrame for testing"""
    data = {
        'Time': [0.1, 0.2, 0.3, 0.4, 0.5],
        'Speed': [2.0, 3.5, 4.0, 3.8, 3.0],
        'Acceleration': [1.0, 0.5, -2.0, -0.5, 0.2], # 0.3秒处有明显的制动
        'Power': [100, 200, 350, 300, 150],           # 0.3秒处为峰值功率
        'frame_number': [10, 20, 30, 40, 50]
    }
    return pd.DataFrame(data)

def test_detect_anomalies_braking(sample_sprint_df):
    """Test whether it can accurately identify abnormal braking force"""
    processor = SprintDataProcessor("mock.csv", "mock.json")
    anomalies = processor.detect_anomalies(sample_sprint_df)
    
    # Verify whether ‘Significant Braking Force’ has been detected.
    braking_events = [a for a in anomalies if a['label'] == "Significant Braking Force"]
    assert len(braking_events) > 0
    assert braking_events[0]['frame'] == 30

def test_detect_anomalies_peak_power(sample_sprint_df):
    """Test whether it can accurately identify peak power output"""
    processor = SprintDataProcessor("mock.csv", "mock.json")
    anomalies = processor.detect_anomalies(sample_sprint_df)
    
    # Verify whether "Peak Power Output" has been detected.
    power_events = [a for a in anomalies if a['label'] == "Peak Power Output"]
    assert len(power_events) == 1
    assert power_events[0]['description'].contains("350.0 W")


# --- Mocking Gemini API ---

@patch('main.genai.Client')
def test_analyzer_initialization(mock_client):
    """Test whether the Analyzer can correctly handle situations where the API Key is missing"""
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'test_key'}):
        analyzer = AthleraAnalyzer()
        assert analyzer.model_name == "gemini-3-flash-preview"

def test_pdf_extraction_empty_folder(tmp_path):
    """Testing the system's robustness when the PDF folder is empty"""
    analyzer = AthleraAnalyzer()
    # 使用 pytest 提供的临时目录 tmp_path
    empty_dir = tmp_path / "empty_pdfs"
    empty_dir.mkdir()
    
    result = analyzer.extract_pdf_knowledge(str(empty_dir))
    assert result == "No biomechanics documentation provided."

# --- Edge Case ---

def test_processor_with_empty_data():
    """Test when data is empty, whether the algorithm crashes"""
    empty_df = pd.DataFrame(columns=['Time', 'Speed', 'Acceleration', 'Power', 'frame_number'])
    processor = SprintDataProcessor("mock.csv", "mock.json")
    
    # 逻辑上空数据不应产生异常，也不应报错
    anomalies = processor.detect_anomalies(empty_df)
    assert isinstance(anomalies, list)
    assert len(anomalies) == 0