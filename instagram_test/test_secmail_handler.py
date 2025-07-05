from secmail_handler import SecMail

def main():
    mail = SecMail()
    print("📧 生成されたメールアドレス:", mail.get_email_address())
    print("📩 Instagramなどからの認証コードを受信待機中...（最大5分）")

    code = mail.get_verification_code()
    if code:
        print("✅ 認証コード取得成功:", code)
    else:
        print("❌ 認証コード取得失敗（時間切れ or メール未着）")

if __name__ == "__main__":
    main()
