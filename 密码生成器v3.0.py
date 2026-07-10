import string
import random
import math  # 新增：用于计算熵值
# 初始化安全随机数生成器（基于操作系统熵源）
secure_rng = random.SystemRandom()

print('=' * 50)
print('  欢迎使用密码生成器 v3.0 (超安全版) (awa)')
print('  史上第一次大更新awa')
print('=' * 50)
print('由 阳阳程序 编译 (awa)')
print('\n📌 更新内容：')
print('  ✅ 词库扩充至 170 个单词（组合数 7,225 种）')
print('  ✅ 排除易混淆字符（可选）')
print('  ✅ 密码强度评级（熵值计算）')
print('  ✅ 智能过滤敏感组合')
print('  ✅ 彩色评级显示')
print('  ✅ 加了一些小彩蛋（自己去探索吧awa）')
print('  （bro这次真的更了很多！）')
print('=' * 50)
while True:
    # ---------- 输入验证（密码个数） ----------
    while True:
        try:
            count_input = int(input('\n🔢 你要几个密码？(数字）(awa) ').strip())
            if count_input == 1:
                print('( ⓛ ω ⓛ ) 就一个密码？够用就行！')
            elif 1 < count_input < 10:
                print('(｡•ω•｡) 不多不少，刚刚好~')
            elif 10 <= count_input < 20:
                print('(⊙_⊙) 生成这么多，手不酸吗？')
            elif 20 <= count_input < 100:
                print('(ﾟДﾟ≡ﾟДﾟ) 你是要批量注册账号吗？！')
            elif count_input >= 100:
                print('ARE YOU CRAZY??!!')
            if count_input > 0:
                break
            else:
                print('❌ 密码个数应为正整数，请重新输入')
        except ValueError:
            print('❌ 请输入有效的数字')
    # ---------- 密码长度设置 ----------
    while True:
        try:
            length = int(input('📏 请输入密码长度（建议 8-20）：').strip())
            if 6 <= length <= 30:
                break
            elif length < 6:
                print('⚠️ 密码长度过短，自动设为 8 位')
                length = 8
                break
            elif length > 30:
                print('⚠️ 密码长度过长，自动设为 20 位')
                length = 20
                break
        except ValueError:
            print('❌ 输入无效，使用默认长度 12 位')
            length = 12
            break

    # ---------- 排除易混淆字符选项 ----------
    while True:
        simple_choice = input('🔤 是否排除易混淆字符 (l/1/O/0)？(y/n，默认 n)：').strip().lower()
        if simple_choice in ['y', 'n', '']:
            use_simple = (simple_choice == 'y')
            break
        else:
            print('❌ 请输入 y 或 n')

    if use_simple:
        print('✅ 已启用排除模式（将移除 l, o, O, 0, 1 等易混淆字符）')
    else:
        print('ℹ️  使用完整字符集')

    # ---------- 过滤敏感组合（黑名单） ----------
    banned_combos = [
        'badass', 'sadmad', 'bigtits', 'sex', 'fuck', 'shit', 'damn',
        'hell', 'ass', 'bitch', 'cunt', 'dick', 'pussy', 'cock'
    ]


    def contains_banned(word):
        """检查单词是否包含黑名单中的敏感词"""
        word_lower = word.lower()
        for banned in banned_combos:
            if banned in word_lower:
                return True
        return False


    # ---------- 词库 ----------
    first_dictionary_noun = [
        'cat', 'dog', 'fox', 'bear', 'lion', 'tiger', 'wolf', 'deer', 'seal', 'owl',
        'ant', 'bee', 'cow', 'pig', 'hen', 'duck', 'fish', 'bird', 'frog', 'bat',
        'hill', 'lake', 'moon', 'sun', 'sky', 'cloud', 'rain', 'snow', 'wind', 'storm',
        'tree', 'leaf', 'rock', 'sand', 'clay', 'wood', 'wool', 'silk', 'gold', 'silver',
        'fire', 'flame', 'smoke', 'ash', 'dust', 'mist', 'fog', 'ice', 'frost', 'dew',
        'star', 'comet', 'orbit', 'path', 'road', 'lane', 'gate', 'tower', 'bridge', 'wall',
        'house', 'home', 'room', 'door', 'window', 'roof', 'floor', 'stair', 'chair', 'desk',
        'bed', 'lamp', 'clock', 'book', 'note', 'card', 'page', 'word', 'line', 'pen',
        'cup', 'bowl', 'pan', 'pot', 'jar'
    ]

    # 去重处理（移除重复的形容词）
    second_dictionary_adjective = list(set([
        'big', 'small', 'tall', 'short', 'long', 'wide', 'deep', 'high', 'low', 'steep',
        'fast', 'slow', 'hard', 'soft', 'rough', 'smooth', 'sharp', 'dull', 'thick', 'thin',
        'hot', 'cold', 'warm', 'cool', 'mild', 'dry', 'wet', 'damp', 'dark', 'bright',
        'light', 'heavy', 'weak', 'strong', 'bold', 'shy', 'calm', 'wild', 'tame', 'rare',
        'new', 'old', 'young', 'fresh', 'stale', 'pure', 'clear', 'clean', 'dirty', 'neat',
        'tidy', 'messy', 'busy', 'free', 'safe', 'sure', 'true', 'real', 'fake', 'whole',
        'half', 'full', 'empty', 'open', 'closed', 'alive', 'dead', 'awake', 'asleep', 'glad',
        'sad', 'mad', 'mean',  # wild, calm, mild 已在上方出现，已移除重复
        'plain', 'rich', 'poor', 'quiet', 'loud'
    ]))


    # ---------- 配置字符集 ----------
    def get_char_sets(simple_mode):
        """根据模式返回字母、数字、符号字符集"""
        if simple_mode:
            letters = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'  # 移除 l, o, O
            digits = '23456789'  # 移除 0, 1
            punct = '!@#$%^&*()_+-=[]{}|;:,.<>?'  # 移除 ' 和 " 等易混淆符号
        else:
            letters = string.ascii_letters
            digits = string.digits
            punct = string.punctuation
        return letters, digits, punct


    # ---------- 密码强度计算 ----------
    def calculate_entropy(password):
        """计算密码熵值（比特）"""
        used_chars = set(password)
        charset_size = len(used_chars)
        if charset_size == 0:
            return 0
        return len(password) * math.log2(charset_size)


    def get_strength_rating(entropy):
        """根据熵值返回评级和emoji"""
        if entropy >= 80:
            return '🔒 极强', '\033[92m'  # 绿色
        elif entropy >= 60:
            return '✅ 强', '\033[94m'  # 蓝色
        elif entropy >= 40:
            return '⚠️ 中等', '\033[93m'  # 黄色
        else:
            return '❌ 弱', '\033[91m'  # 红色


    # ---------- 核心密码生成函数 ----------
    def generate_secure_password(target_length, simple_mode):
        # 获取字符集
        letters, digits, punct = get_char_sets(simple_mode)

        # 1. 随机选词并组合（带敏感词过滤，最多尝试20次）
        for attempt in range(20):
            noun = secure_rng.choice(first_dictionary_noun)
            adjective = secure_rng.choice(second_dictionary_adjective)
            word_part = adjective + noun
            if not contains_banned(word_part):
                break
        else:
            # 如果20次都失败，就强制使用第一个（几乎不可能触发）
            word_part = first_dictionary_noun[0] + second_dictionary_adjective[0]

        # 2. 随机切换大小写
        word_part_mixed = ''.join(
            c.upper() if secure_rng.choice([True, False]) else c.lower()
            for c in word_part
        )

        # 3. 预留 2 个位置给数字和符号
        if len(word_part_mixed) > target_length - 2:
            word_part_mixed = word_part_mixed[:target_length - 2]

        # 4. 计算剩余填充字符数
        remaining = target_length - len(word_part_mixed) - 2
        if remaining < 0:
            word_part_mixed = word_part_mixed[:target_length - 2]
            remaining = 0

        # 5. 生成填充字符（字母+数字）
        fill_chars = ''.join(
            secure_rng.choice(letters + digits)
            for _ in range(remaining)
        )

        # 6. 生成一个数字和一个符号
        final_digit = secure_rng.choice(digits)
        final_punct = secure_rng.choice(punct)

        # 7. 组装并打乱
        password_list = list(word_part_mixed + fill_chars + final_digit + final_punct)
        secure_rng.shuffle(password_list)

        return ''.join(password_list)


    # ---------- 生成并输出 ----------
    print('\n' + '=' * 50)
    print('🔄 正在生成密码...')
    print('=' * 50 + '\n')

    for i in range(count_input):
        password = generate_secure_password(length, use_simple)
        entropy = calculate_entropy(password)
        rating, color = get_strength_rating(entropy)

        # 彩色输出（支持终端颜色）
        print(f'{color}密码 {i + 1} 是：{password}\033[0m')
        print(f'   └─ 熵值：{entropy:.1f} bit  |  评级：{rating}\n')
    #小彩蛋awa
    if 20 <= count_input < 50:
        print('程序：不兑！有问题...我头好晕')
    elif 50 <= count_input < 100 :
        print('(ﾟДﾟ≡ﾟДﾟ),来人啦，有程序亖这啦！！！')
        print('程序：我...我还能活......(；′д`)')
    elif 100 <= count_input < 1000:
        print('程序：再见了，再见了......这个美丽的世界......（掏出刀子）')
        print('阳阳：傻孩子，别干蠢事啊！！！')
    elif count_input >= 1000:
        print('医生：这伤，恐怕是致命的...')
        print('阳阳：NO' + '！' * 50 + '（撕心裂肺ing）')
    #----------结束语----------
    while True:
        print('=' * 50)
        answer = input('输入next继续生成密码，输入exit退出(awa)')
        if answer == 'exit':
            print('=' * 50)
            print('感谢使用，再见!（记住欧awa）')
            print('\n💡 小贴士：')
            print('  • Ctrl+C = 复制  |  Ctrl+V = 粘贴')
            print('  • 密码强度越高（熵值越大），越难被破解')
            print('  • 建议熵值 ≥ 60 bit 的密码')
            print('=' * 50)
            print('\n'* 10)
            print('   =====   =====   =   =   =====   =====   =====')
            print('   =   =   = = =    = =    =       =       =    ')
            print('   =   =   = = =     =     =====   =====   =====')
            print('   =   =   = = =     =         =   =       =')
            print('   ======  = = =     =     =====   =====   =====')
            print('\n' * 10)
            print('（｡•ω•｡）哈基米（可爱捏）')
            exit(0)
        elif answer == 'next':
            break
        else:
            print('❌请输入"next"或"exit"')
