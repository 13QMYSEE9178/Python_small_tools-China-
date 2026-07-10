#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
超级密码生成器 v4.0
功能完整版 - 安全、高效、用户友好
"""

import string
import random
import math
import json
import os
from datetime import datetime
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


# ============ 配置类 ============
@dataclass
class Config:
    """用户配置"""
    default_length: int = 12
    exclude_confusable: bool = False
    min_length: int = 6
    max_length: int = 30
    history_limit: int = 100

    @classmethod
    def load(cls, config_file: str = "password_config.json") -> 'Config':
        """加载配置文件"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls(**data)
            except:
                pass
        return cls()

    def save(self, config_file: str = "password_config.json"):
        """保存配置文件"""
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=2, ensure_ascii=False)


# ============ 密码历史记录 ============
@dataclass
class PasswordRecord:
    """密码记录"""
    password: str
    entropy: float
    timestamp: str
    length: int

    def to_dict(self) -> Dict:
        return {
            'password': self.password,
            'entropy': round(self.entropy, 1),
            'timestamp': self.timestamp,
            'length': self.length
        }


class PasswordHistory:
    """密码历史管理"""

    def __init__(self, limit: int = 100):
        self.history: List[PasswordRecord] = []
        self.limit = limit

    def add(self, record: PasswordRecord):
        """添加记录"""
        self.history.append(record)
        if len(self.history) > self.limit:
            self.history = self.history[-self.limit:]

    def get_last(self, n: int = 10) -> List[PasswordRecord]:
        """获取最近n条记录"""
        return self.history[-n:]

    def clear(self):
        """清空历史"""
        self.history.clear()

    def export(self, filename: str = "password_history.json"):
        """导出历史"""
        data = [record.to_dict() for record in self.history]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ============ 词库管理 ============
class WordDictionary:
    """词库管理类"""

    def __init__(self):
        self.nouns = [
            'cat', 'dog', 'fox', 'bear', 'lion', 'tiger', 'wolf', 'deer', 'seal', 'owl',
            'ant', 'bee', 'cow', 'pig', 'hen', 'duck', 'fish', 'bird', 'frog', 'bat',
            'hill', 'lake', 'moon', 'sun', 'sky', 'cloud', 'rain', 'snow', 'wind', 'storm',
            'tree', 'leaf', 'rock', 'sand', 'clay', 'wood', 'wool', 'silk', 'gold', 'silver',
            'fire', 'flame', 'smoke', 'ash', 'dust', 'mist', 'fog', 'ice', 'frost', 'dew',
            'star', 'comet', 'orbit', 'path', 'road', 'lane', 'gate', 'tower', 'bridge', 'wall',
            'house', 'home', 'room', 'door', 'window', 'roof', 'floor', 'stair', 'chair', 'desk',
            'bed', 'lamp', 'clock', 'book', 'note', 'card', 'page', 'word', 'line', 'pen',
            'cup', 'bowl', 'pan', 'pot', 'jar', 'mug', 'plate', 'knife', 'fork', 'spoon'
        ]

        # 使用 dict.fromkeys 去重并保持顺序
        self.adjectives = list(dict.fromkeys([
            'big', 'small', 'tall', 'short', 'long', 'wide', 'deep', 'high', 'low', 'steep',
            'fast', 'slow', 'hard', 'soft', 'rough', 'smooth', 'sharp', 'dull', 'thick', 'thin',
            'hot', 'cold', 'warm', 'cool', 'mild', 'dry', 'wet', 'damp', 'dark', 'bright',
            'light', 'heavy', 'weak', 'strong', 'bold', 'shy', 'calm', 'wild', 'tame', 'rare',
            'new', 'old', 'young', 'fresh', 'stale', 'pure', 'clear', 'clean', 'dirty', 'neat',
            'tidy', 'messy', 'busy', 'free', 'safe', 'sure', 'true', 'real', 'fake', 'whole',
            'half', 'full', 'empty', 'open', 'closed', 'alive', 'dead', 'awake', 'asleep', 'glad',
            'sad', 'mad', 'mean', 'kind', 'nice', 'good', 'bad', 'ugly', 'pretty',
            'plain', 'rich', 'poor', 'quiet', 'loud', 'happy', 'silly', 'smart'
        ]))

    def get_random_noun(self) -> str:
        """随机获取名词"""
        return random.SystemRandom().choice(self.nouns)

    def get_random_adjective(self) -> str:
        """随机获取形容词"""
        return random.SystemRandom().choice(self.adjectives)


# ============ 核心密码生成器 ============
class PasswordGenerator:
    """密码生成器核心类"""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.secure_rng = random.SystemRandom()
        self.word_dict = WordDictionary()
        self.history = PasswordHistory(self.config.history_limit)

        # 敏感词黑名单
        self.banned_combos = [
            'badass', 'sadmad', 'bigtits', 'sex', 'fuck', 'shit', 'damn',
            'hell', 'ass', 'bitch', 'cunt', 'dick', 'pussy', 'cock',
            'penis', 'vagina', 'anal', 'boob', 'tits'
        ]

        # 字符集缓存
        self._char_sets_cache = {}

    def get_char_sets(self, simple_mode: bool) -> Tuple[str, str, str]:
        """获取字符集（带缓存）"""
        cache_key = simple_mode
        if cache_key in self._char_sets_cache:
            return self._char_sets_cache[cache_key]

        if simple_mode:
            # 移除易混淆字符：l, o, O, 0, 1
            letters = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
            digits = '23456789'
            punct = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        else:
            letters = string.ascii_letters
            digits = string.digits
            punct = string.punctuation

        self._char_sets_cache[cache_key] = (letters, digits, punct)
        return letters, digits, punct

    def contains_banned(self, word: str) -> bool:
        """检查是否包含敏感词"""
        word_lower = word.lower()
        return any(banned in word_lower for banned in self.banned_combos)

    def calculate_entropy(self, password: str) -> float:
        """计算密码熵值"""
        if not password:
            return 0.0
        used_chars = set(password)
        charset_size = len(used_chars)
        if charset_size == 0:
            return 0.0
        return len(password) * math.log2(charset_size)

    def get_strength_rating(self, entropy: float) -> Tuple[str, str, str]:
        """
        获取密码强度评级
        返回: (评级文本, 颜色代码, 建议)
        """
        if entropy >= 80:
            return '🔒 极强', '\033[92m', '非常安全，适合重要账号'
        elif entropy >= 60:
            return '✅ 强', '\033[94m', '安全，适合大多数场景'
        elif entropy >= 40:
            return '⚠️ 中等', '\033[93m', '建议增加长度或使用特殊字符'
        else:
            return '❌ 弱', '\033[91m', '不安全，请增加密码复杂度'

    def generate_password(self, length: int, simple_mode: bool = False) -> Tuple[str, Dict]:
        """
        生成单个密码
        返回: (密码, 元数据)
        """
        # 验证长度
        if length < 4:
            length = 4
        if length > 100:
            length = 100

        letters, digits, punct = self.get_char_sets(simple_mode)

        # 1. 生成词根（带敏感词过滤）
        word_part = ""
        for attempt in range(30):
            noun = self.word_dict.get_random_noun()
            adjective = self.word_dict.get_random_adjective()
            candidate = adjective + noun
            if not self.contains_banned(candidate):
                word_part = candidate
                break
        else:
            # 保底方案：使用数字和字母组合
            word_part = "".join(self.secure_rng.choices(letters, k=6))

        # 2. 随机大小写混合
        word_part_mixed = ''.join(
            c.upper() if self.secure_rng.choice([True, False]) else c.lower()
            for c in word_part
        )

        # 3. 确保至少包含4类字符各一个
        required_chars = [
            self.secure_rng.choice(letters.lower()),  # 小写字母
            self.secure_rng.choice(letters.upper()),  # 大写字母
            self.secure_rng.choice(digits),  # 数字
            self.secure_rng.choice(punct)  # 符号
        ]

        # 4. 计算剩余空间
        base_length = len(word_part_mixed) + 4  # 词根 + 4个必需字符
        remaining = length - base_length

        # 如果剩余空间不足，截断词根
        if remaining < 0:
            word_part_mixed = word_part_mixed[:max(0, length - 4)]
            remaining = length - len(word_part_mixed) - 4

        # 5. 生成填充字符
        fill_chars = ''.join(
            self.secure_rng.choice(letters + digits)
            for _ in range(max(0, remaining))
        )

        # 6. 组装
        password_list = list(word_part_mixed + fill_chars)
        # 在随机位置插入必需字符
        for char in required_chars:
            pos = self.secure_rng.randint(0, len(password_list))
            password_list.insert(pos, char)

        # 7. 最终打乱
        self.secure_rng.shuffle(password_list)
        password = ''.join(password_list)

        # 8. 计算元数据
        entropy = self.calculate_entropy(password)
        rating, color, suggestion = self.get_strength_rating(entropy)

        metadata = {
            'entropy': entropy,
            'rating': rating,
            'color': color,
            'suggestion': suggestion,
            'length': len(password),
            'simple_mode': simple_mode
        }

        # 记录历史
        record = PasswordRecord(
            password=password,
            entropy=entropy,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            length=len(password)
        )
        self.history.add(record)

        return password, metadata

    def generate_passwords(self, count: int, length: int, simple_mode: bool = False) -> List[Tuple[str, Dict]]:
        """批量生成密码"""
        results = []
        for _ in range(count):
            results.append(self.generate_password(length, simple_mode))
        return results

    def check_weak_passwords(self) -> List[str]:
        """检查常见弱密码（仅示例）"""
        common_weak = [
            '123456', 'password', '123456789', '12345', '12345678',
            'qwerty', 'abc123', 'password1', '1234567', '111111'
        ]
        return common_weak


# ============ 界面交互 ============
class PasswordGeneratorUI:
    """用户界面"""

    def __init__(self):
        self.generator = PasswordGenerator()
        self.config = self.generator.config
        self._setup_console()

    def _setup_console(self):
        """设置控制台"""
        # 检测是否支持颜色
        self.supports_color = True
        if os.name == 'nt':  # Windows
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                self.supports_color = False

    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """打印标题"""
        self.clear_screen()
        print('=' * 60)
        print('  🔐 欢迎使用密码生成器 v3.5  (Demo测试版)（awa）')
        print('   史上第二次大更新 awa')
        print('  ⚠ v3.5只作为测试尝鲜版，整体运行尚不稳定，v4.0上线后，将停止维护该版本 ⚠')
        print('  Tip:如果您追求稳定与有趣，推荐使用v3.0完整版本 awa')
        print('=' * 60)
        print('本程序由 阳阳程序 编译awa')
        print('  ✨ 更新内容/特性:')
        print('     • 加密级随机数生成 (SystemRandom)')
        print('     • 智能密码强度评估 (熵值计算)')
        print('     • 自动排除易混淆字符')
        print('     • 敏感词自动过滤')
        print('     • 密码历史记录')
        print('     • 配置文件持久化')
        print('     • 增加了防伪标志')
        print('     • 程序停止时不再报错')
        print('=' * 60)
        print()

    def print_footer(self):
        """打印底部信息"""
        print()
        print('=' * 60)
        print('  💡 安全提示:')
        print('     • 建议密码长度 ≥ 12 位')
        print('     • 熵值 ≥ 60 bit 为安全密码')
        print('     • 不要在多个网站使用相同密码')
        print('     • 定期更换重要账号密码')
        print('=' * 60)

    def print_password_with_rating(self, index: int, password: str, metadata: Dict):
        """打印带评级的密码"""
        color = metadata['color']
        entropy = metadata['entropy']
        rating = metadata['rating']
        suggestion = metadata['suggestion']

        print(f'\n{color}📝 密码 #{index + 1}: {password}\033[0m')
        print(f'   ├─ 熵值: {entropy:.1f} bit')
        print(f'   ├─ 评级: {rating}')
        print(f'   └─ 建议: {suggestion}')

    def get_user_input(self) -> Tuple[int, int, bool]:
        """获取用户输入"""
        # 密码数量
        while True:
            try:
                count = int(input('\n🔢 请输入要生成的密码数量: ').strip())
                if count > 0:
                    # 彩蛋提示
                    if count == 1:
                        print('(｡•ω•｡) 精选单密码！')
                    elif 2 <= count <= 5:
                        print('(◕‿◕) 适量生成，明智之选！')
                    elif 6 <= count <= 20:
                        print('(⊙_⊙) 何意味！')
                    elif 21 <= count <= 50:
                        print('(ﾟДﾟ) 你这是要开密码库吗？！')
                    elif count > 50:
                        print('⚠️  WTF!!!!!!!!!!!')
                    break
                else:
                    print('❌ 请输入正整数')
            except ValueError:
                print('❌ 请输入有效的数字')

        # 密码长度
        while True:
            try:
                length_input = input(f'📏 请输入密码长度 (建议 12-20, 默认 {self.config.default_length}): ').strip()
                if not length_input:
                    length = self.config.default_length
                    break

                length = int(length_input)
                if 4 <= length <= 100:
                    break
                elif length < 4:
                    print('⚠️  太短了，自动设为 8 位')
                    length = 8
                    break
                else:
                    print('⚠️  太长了，自动设为 30 位')
                    length = 30
                    break
            except ValueError:
                print('❌ 请输入有效数字，使用默认长度')
                length = self.config.default_length
                break

        # 排除易混淆字符
        while True:
            simple_input = input('🔤 排除易混淆字符 (l/1/O/0)？(y/n，默认 n): ').strip().lower()
            if simple_input in ['y', 'n', '']:
                simple_mode = (simple_input == 'y')
                break
            else:
                print('❌ 请输入 y 或 n')

        return count, length, simple_mode

    def show_history(self):
        """显示历史记录"""
        history = self.generator.history.get_last(10)
        if not history:
            print('\n📭 暂无密码历史记录')
            return

        print('\n📜 最近生成的密码 (最多10条):')
        print('-' * 60)
        for i, record in enumerate(history, 1):
            print(f'{i:2}. {record.password[:20]:<20} | 熵值: {record.entropy:.1f} bit | {record.timestamp}')
        print('-' * 60)

    def export_history(self):
        """导出历史"""
        try:
            self.generator.history.export()
            print('✅ 历史记录已导出到 password_history.json')
        except Exception as e:
            print(f'❌ 导出失败: {e}')

    def run(self):
        """主运行循环"""
        while True:
            self.print_header()

            # 获取用户输入
            count, length, simple_mode = self.get_user_input()

            # 显示配置
            print('\n' + '=' * 60)
            print(f'⚙️  生成配置:')
            print(f'   • 数量: {count} 个')
            print(f'   • 长度: {length} 位')
            print(f'   • 排除易混淆: {"是" if simple_mode else "否"}')
            print('=' * 60)

            # 生成密码
            print('\n🔄 正在生成密码...\n')

            results = self.generator.generate_passwords(count, length, simple_mode)

            # 显示结果
            for i, (password, metadata) in enumerate(results):
                self.print_password_with_rating(i, password, metadata)

            # 统计信息
            avg_entropy = sum(m['entropy'] for _, m in results) / len(results) if results else 0
            print(f'\n📊 统计: 平均熵值 = {avg_entropy:.1f} bit | 生成时间: {datetime.now().strftime("%H:%M:%S")}')

            # 彩蛋系统
            self._show_easter_egg(count)

            # 操作菜单
            self._show_action_menu()

    def _show_easter_egg(self, count: int):
        """彩蛋系统"""
        if 20 <= count < 50:
            print('\n🤖 程序: "生成这么多密码，我有点晕..."')
        elif 50 <= count < 100:
            print('\n(ﾟДﾟ≡ﾟДﾟ) 来人啊，有入亖这了！！！')
            print('💻 程序: "我...我还能活..."')
        elif 100 <= count < 500:
            print('\n 程序: "再见了，这个美丽的世界...（掏出刀子)')
            print('💻 系统: "别别别，坚持住！"')
        elif count >= 500:
            print('\n 医生: "这伤，恐怕是致命的..."')
            print('👨 阳阳: "NO' + '!' * 50 +'（撕心裂肺ing）"')

    def _show_action_menu(self):
        """显示操作菜单"""
        while True:
            print('\n' + '-' * 60)
            print('  [1] 继续生成密码')
            print('  [2] 查看历史记录')
            print('  [3] 导出历史记录')
            print('  [4] 重置配置')
            print('  [5] 退出程序')
            print('-' * 60)

            choice = input('请选择操作 (1-5): ').strip()

            if choice == '1':
                break
            elif choice == '2':
                self.show_history()
                input('\n按 Enter 继续...')
                self.clear_screen()
                break
            elif choice == '3':
                self.export_history()
                input('\n按 Enter 继续...')
                self.clear_screen()
                break
            elif choice == '4':
                self.config = Config()
                self.generator.config = self.config
                self.config.save()
                print('✅ 配置已重置')
                input('\n按 Enter 继续...')
                self.clear_screen()
                break
            elif choice == '5':
                self._exit_program()
            else:
                print('❌ 无效选项，请重新选择')

    def _exit_program(self):
        """退出程序"""
        self.clear_screen()
        print('=' * 60)
        print('  👋 感谢使用密码生成器！')
        print('=' * 60)
        print('\n  🔐 安全提醒:')
        print('     • 请将生成的密码保存在安全的地方')
        print('     • 推荐使用密码管理器 (如: Bitwarden, 1Password)')
        print('     • 开启双因素认证 (2FA) 增加安全性')
        print('\n  (｡•ω•｡) 再见，祝您网络安全！')
        print('=' * 60)

        # 打印艺术字
        print('\n' * 10)
        print('   =====   =====   =   =   =====   =====   =====')
        print('   =   =   = = =    = =    =       =       =    ')
        print('   =   =   = = =     =     =====   =====   =====')
        print('   =   =   = = =     =         =   =       =    ')
        print('   ======  = = =     =     =====   =====   =====')
        print('\n' * 10)
        print('（｡•ω•｡）哈基米（可爱捏）')
        exit(0)


# ============ 主程序入口 ============
def main():
    """主程序入口"""
    try:
        ui = PasswordGeneratorUI()
        ui.run()
    except KeyboardInterrupt:
        print('\n\n👋 再见！')
        sys.exit(0)
    except Exception as e:
        print(f'\n❌ 发生错误: {e}')
        print('请重启程序')
        sys.exit(1)


if __name__ == '__main__':
    import sys

    main()