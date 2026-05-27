#!/usr/bin/env python3
"""
Browser Automation - 浏览器自动化模块
基于Hermes Agent的完整浏览器控制理念，提供网页操作、数据提取和自动化测试功能

核心功能：
1. 网页浏览和导航
2. 内容提取和解析
3. 表单填写和提交
4. 截图和视觉分析
5. 交互式操作模拟
"""

import os
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import base64
import hashlib

# 尝试导入 Playwright（可选）
try:
    import playwright
    from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("[警告] Playwright 未安装，浏览器自动化功能受限")

# 尝试导入 Selenium（可选）
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[警告] Selenium 未安装，浏览器自动化功能受限")

# 尝试导入 BeautifulSoup（可选）
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    print("[警告] BeautifulSoup 未安装，内容提取功能受限")

class BrowserAutomationError(Exception):
    """浏览器自动化错误"""
    pass

class WebElement:
    """网页元素封装"""
    
    def __init__(self, selector: str, content: str = "", attributes: Dict[str, str] = None):
        self.selector = selector
        self.content = content
        self.attributes = attributes or {}
        self.element_type = self._detect_type()
    
    def _detect_type(self) -> str:
        """检测元素类型"""
        selector_lower = self.selector.lower()
        if "input" in selector_lower:
            return "input"
        elif "button" in selector_lower:
            return "button"
        elif "a" in selector_lower and "href" in self.attributes:
            return "link"
        elif "img" in selector_lower:
            return "image"
        elif "select" in selector_lower:
            return "dropdown"
        elif "textarea" in selector_lower:
            return "textarea"
        else:
            return "element"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "selector": self.selector,
            "content": self.content,
            "attributes": self.attributes,
            "type": self.element_type
        }
    
    def __str__(self) -> str:
        return f"<WebElement {self.element_type}: {self.selector}>"

class BrowserAutomator:
    """浏览器自动化器"""
    
    def __init__(self, browser_type: str = "chromium", headless: bool = True):
        self.browser_type = browser_type
        self.headless = headless
        
        # 初始化状态
        self.browser = None
        self.page = None
        self.current_url = None
        self.session_id = f"browser_{int(time.time())}"
        
        # 操作历史
        self.history: List[Dict[str, Any]] = []
        
        # 截图目录
        self.screenshot_dir = Path(".workbuddy/browser_screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[浏览器] 自动化器初始化: {self.browser_type} (headless={self.headless})")
    
    def start(self) -> bool:
        """启动浏览器"""
        if PLAYWRIGHT_AVAILABLE:
            return self._start_with_playwright()
        elif SELENIUM_AVAILABLE:
            return self._start_with_selenium()
        else:
            print("[错误] 没有可用的浏览器自动化库")
            return False
    
    def _start_with_playwright(self) -> bool:
        """使用Playwright启动浏览器"""
        try:
            self.playwright = sync_playwright().start()
            
            # 选择浏览器类型
            if self.browser_type == "chromium":
                browser_launcher = self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                browser_launcher = self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                browser_launcher = self.playwright.webkit.launch(headless=self.headless)
            else:
                browser_launcher = self.playwright.chromium.launch(headless=self.headless)
            
            self.browser = browser_launcher
            self.page = self.browser.new_page()
            
            self._record_operation("start_browser", {"type": self.browser_type})
            return True
        
        except Exception as e:
            print(f"[错误] Playwright启动失败: {e}")
            return False
    
    def _start_with_selenium(self) -> bool:
        """使用Selenium启动浏览器"""
        try:
            if self.browser_type == "chrome":
                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.browser = webdriver.Chrome(options=options)
            elif self.browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                self.browser = webdriver.Firefox(options=options)
            else:
                self.browser = webdriver.Chrome(options=webdriver.ChromeOptions())
            
            self._record_operation("start_browser", {"type": self.browser_type})
            return True
        
        except Exception as e:
            print(f"[错误] Selenium启动失败: {e}")
            return False
    
    def navigate_to(self, url: str, wait_seconds: int = 5) -> bool:
        """导航到URL"""
        if not self.browser:
            print("[错误] 浏览器未启动")
            return False
        
        try:
            if PLAYWRIGHT_AVAILABLE and self.page:
                self.page.goto(url)
                self.current_url = self.page.url
            elif SELENIUM_AVAILABLE and self.browser:
                self.browser.get(url)
                self.current_url = self.browser.current_url
            else:
                return False
            
            time.sleep(wait_seconds)  # 等待页面加载
            self._record_operation("navigate", {"url": url, "wait": wait_seconds})
            return True
        
        except Exception as e:
            print(f"[错误] 导航失败: {e}")
            return False
    
    def get_page_content(self) -> Optional[str]:
        """获取页面内容"""
        if not self.browser:
            return None
        
        try:
            if PLAYWRIGHT_AVAILABLE and self.page:
                content = self.page.content()
            elif SELENIUM_AVAILABLE and self.browser:
                content = self.browser.page_source
            else:
                return None
            
            self._record_operation("get_content", {"url": self.current_url, "length": len(content)})
            return content
        
        except Exception as e:
            print(f"[错误] 获取内容失败: {e}")
            return None
    
    def extract_elements(self, selector: str = None) -> List[WebElement]:
        """提取网页元素"""
        content = self.get_page_content()
        if not content:
            return []
        
        elements = []
        
        if BEAUTIFULSOUP_AVAILABLE:
            soup = BeautifulSoup(content, 'html.parser')
            
            if selector:
                # 根据选择器提取元素
                found_elements = soup.select(selector)
            else:
                # 提取常用元素类型
                found_elements = []
                for tag_name in ['a', 'input', 'button', 'img', 'form', 'div', 'span']:
                    found_elements.extend(soup.find_all(tag_name))
            
            for element in found_elements:
                # 构建元素选择器
                element_selector = self._build_element_selector(element)
                
                # 提取属性和内容
                attrs = dict(element.attrs)
                content_text = element.get_text(strip=True)
                
                web_element = WebElement(
                    selector=element_selector,
                    content=content_text,
                    attributes=attrs
                )
                elements.append(web_element)
        
        self._record_operation("extract_elements", {
            "selector": selector,
            "count": len(elements)
        })
        
        return elements
    
    def _build_element_selector(self, element) -> str:
        """为BeautifulSoup元素构建CSS选择器"""
        if hasattr(element, 'name'):
            selector = element.name
            
            # 添加ID
            if element.get('id'):
                selector += f"#{element['id']}"
            
            # 添加类
            if element.get('class'):
                classes = '.'.join(element['class'])
                selector += f".{classes}"
            
            # 添加其他属性（简化版）
            for attr_name, attr_value in element.attrs.items():
                if attr_name not in ['id', 'class'] and attr_value:
                    selector += f"[{attr_name}='{attr_value}']"
            
            return selector
        return "unknown"
    
    def take_screenshot(self, filename: str = None, full_page: bool = True) -> Optional[str]:
        """截图"""
        if not self.browser:
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = self.screenshot_dir / filename
            
            if PLAYWRIGHT_AVAILABLE and self.page:
                if full_page:
                    screenshot = self.page.screenshot(path=str(screenshot_path), full_page=True)
                else:
                    screenshot = self.page.screenshot(path=str(screenshot_path))
            
            elif SELENIUM_AVAILABLE and self.browser:
                self.browser.save_screenshot(str(screenshot_path))
            
            else:
                return None
            
            self._record_operation("take_screenshot", {
                "path": str(screenshot_path),
                "full_page": full_page
            })
            
            return str(screenshot_path)
        
        except Exception as e:
            print(f"[错误] 截图失败: {e}")
            return None
    
    def click_element(self, selector: str, wait_seconds: int = 3) -> bool:
        """点击元素"""
        if not self.browser:
            return False
        
        try:
            if PLAYWRIGHT_AVAILABLE and self.page:
                self.page.click(selector)
            elif SELENIUM_AVAILABLE and self.browser:
                element = self.browser.find_element(By.CSS_SELECTOR, selector)
                element.click()
            else:
                return False
            
            time.sleep(wait_seconds)
            self._record_operation("click", {"selector": selector})
            return True
        
        except Exception as e:
            print(f"[错误] 点击失败: {e}")
            return False
    
    def fill_form(self, selector: str, value: str, submit: bool = False) -> bool:
        """填写表单"""
        if not self.browser:
            return False
        
        try:
            if PLAYWRIGHT_AVAILABLE and self.page:
                self.page.fill(selector, value)
                if submit:
                    self.page.press(selector, "Enter")
            
            elif SELENIUM_AVAILABLE and self.browser:
                element = self.browser.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(value)
                if submit:
                    element.send_keys(Keys.RETURN)
            
            else:
                return False
            
            self._record_operation("fill_form", {"selector": selector, "value": value})
            return True
        
        except Exception as e:
            print(f"[错误] 表单填写失败: {e}")
            return False
    
    def execute_script(self, script: str) -> Optional[Any]:
        """执行JavaScript脚本"""
        if not self.browser:
            return None
        
        try:
            if PLAYWRIGHT_AVAILABLE and self.page:
                result = self.page.evaluate(script)
            elif SELENIUM_AVAILABLE and self.browser:
                result = self.browser.execute_script(script)
            else:
                return None
            
            self._record_operation("execute_script", {"script": script[:50] + "..." if len(script) > 50 else script})
            return result
        
        except Exception as e:
            print(f"[错误] 执行脚本失败: {e}")
            return None
    
    def get_page_info(self) -> Dict[str, Any]:
        """获取页面信息"""
        content = self.get_page_content()
        
        info = {
            "url": self.current_url,
            "content_length": len(content) if content else 0,
            "session_id": self.session_id,
            "operations": len(self.history),
            "screenshot_count": len(list(self.screenshot_dir.glob("*.png"))),
            "automation_lib": "playwright" if PLAYWRIGHT_AVAILABLE else "selenium" if SELENIUM_AVAILABLE else "none"
        }
        
        if content and BEAUTIFULSOUP_AVAILABLE:
            soup = BeautifulSoup(content, 'html.parser')
            info.update({
                "title": soup.title.string if soup.title else "",
                "link_count": len(soup.find_all('a')),
                "form_count": len(soup.find_all('form')),
                "image_count": len(soup.find_all('img'))
            })
        
        return info
    
    def close(self):
        """关闭浏览器"""
        try:
            if PLAYWRIGHT_AVAILABLE and self.browser:
                self.browser.close()
                self.playwright.stop()
            elif SELENIUM_AVAILABLE and self.browser:
                self.browser.quit()
            
            self.browser = None
            self.page = None
            self._record_operation("close_browser", {})
        
        except Exception as e:
            print(f"[错误] 关闭浏览器失败: {e}")
    
    def _record_operation(self, operation_type: str, details: Dict[str, Any]):
        """记录操作"""
        operation = {
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "url": self.current_url
        }
        self.history.append(operation)
    
    def save_session_report(self) -> str:
        """保存会话报告"""
        report = {
            "session_id": self.session_id,
            "browser_type": self.browser_type,
            "start_time": self.history[0]["timestamp"] if self.history else datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "operations": self.history,
            "page_info": self.get_page_info(),
            "screenshots": [str(p) for p in self.screenshot_dir.glob("*.png")]
        }
        
        report_file = self.screenshot_dir / f"session_{self.session_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(report_file)

def demo_browser_automation():
    """演示浏览器自动化功能"""
    print("[启动] Hermes风格浏览器自动化演示")
    
    # 创建自动化器
    automator = BrowserAutomator(headless=True, browser_type="chromium")
    
    # 启动浏览器
    if not automator.start():
        print("[错误] 无法启动浏览器，跳过演示")
        return
    
    try:
        # 导航到示例网站
        print("[操作] 导航到示例页面...")
        automator.navigate_to("https://example.com", wait_seconds=3)
        
        # 获取页面信息
        page_info = automator.get_page_info()
        print(f"[信息] 页面信息: {page_info}")
        
        # 截图
        screenshot_path = automator.take_screenshot()
        if screenshot_path:
            print(f"[截图] 已保存到: {screenshot_path}")
        
        # 提取元素
        elements = automator.extract_elements("a")
        print(f"[元素] 找到 {len(elements)} 个链接:")
        for element in elements[:5]:  # 只显示前5个
            print(f"  - {element}")
        
        # 执行脚本
        title = automator.execute_script("return document.title;")
        print(f"[脚本] 页面标题: {title}")
        
        # 保存报告
        report_path = automator.save_session_report()
        print(f"[报告] 会话报告: {report_path}")
        
    except Exception as e:
        print(f"[演示] 发生错误: {e}")
    
    finally:
        # 关闭浏览器
        automator.close()
        print("[完成] 浏览器自动化演示完成")

if __name__ == "__main__":
    demo_browser_automation()