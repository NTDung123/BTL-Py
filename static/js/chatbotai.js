// BẬT/TẮT CHATBOX
const chatBubble = document.querySelector(".chat-bubble");
const chatWindow = document.querySelector(".chatwindow");
const closeChatBtn = document.querySelector(".close-chat");
chatBubble.addEventListener("click", () => {
  chatWindow.classList.remove("hidden");
  chatBubble.classList.add("hidden");
});
closeChatBtn.addEventListener("click", () => {
  chatWindow.classList.add("hidden");
  chatBubble.classList.remove("hidden");
});

// GỬI BẰNG PHÍM ENTER
const messageInput = document.querySelector(".inputarea input");
const sendButton = document.querySelector(".inputarea button");
messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendButton.click();
  }
});

// CHAT

const Gemini_KEY = "AIzaSyDUZOw5goKiHcjuaiat03QJJ8p7NfS804c";
const thongtinHuanluyen = `
A. Giới thiệu về Clothing Shop
Chào mừng bạn đến với Clothing Shop!
Đây là một dự án website bán quần áo, được xây dựng bởi các sinh viên như một bài tập thực hành code Python (sử dụng FastAPI và MySQL).
Mục tiêu của dự án này là áp dụng kiến thức lập trình web vào một sản phẩm thực tế.

B. Thông tin sản phẩm
Website của chúng tôi bán đa dạng các sản phẩm thời trang. Dựa trên dữ liệu sản phẩm, chúng tôi có các loại sản phẩm và thương hiệu sau:

- Loại sản phẩm: Chúng tôi bán Áo thun, Áo sơ mi, Áo len, Áo nỉ, Áo khoác, Quần jeans, Quần short, Váy, và Đầm.
- Thương hiệu: Chúng tôi có các sản phẩm từ các thương hiệu lớn như Zara, H&M, Gucci, Puma, Adidas, Nike, và Uniqlo.

C. Danh sách sản phẩm

Áo Thun (6 sản phẩm)

1.Áo thun Nike Sportswear — 350,000 VNĐ — Cotton 100% — Màu: Đen — Size: S,M,L,XL

2.Áo thun Adidas Originals — 320,000 VNĐ — Cotton — Màu: Trắng — Size: M,L,XL

3.Áo thun Puma Classic — 280,000 VNĐ — Cotton pha Spandex — Màu: Xám — Size: S,M,L

4.Áo thun Uniqlo Airism — 250,000 VNĐ — Cotton Airism — Màu: Xanh navy — Size: S,M,L,XL,XXL

5.Áo thun H&M Basic — 250,000 VNĐ — Cotton — Màu: Trắng — Size: S,M,L,XL

6.Áo thun Gucci Logo — 1,300,000 VNĐ — Cotton cao cấp — Màu: Đen — Size: M,L

Quần Jeans (5 sản phẩm)

1.Quần jeans Adidas Slim Fit — 650,000 VNĐ — Denim co giãn — Màu: Xanh đậm — Size: 28–32

2.Quần jeans Nike Destroyed — 720,000 VNĐ — Denim — Màu: Xanh nhạt — Size: 29–32

3.Quần jeans Zara Skinny — 550,000 VNĐ — Denim skinny — Màu: Đen — Size: 26–29

4.Quần jeans H&M Regular — 450,000 VNĐ — Denim regular — Màu: Xanh trung — Size: 30–34

5.Quần jeans Uniqlo Selvedge — 850,000 VNĐ — Denim selvedge — Màu: Xanh indigo — Size: 30–32

Áo Khoác (4 sản phẩm)

1.Áo khoác Zara Basic — 850,000 VNĐ — Kaki — Màu: Be — Size: S,M,L

2.Áo khoác Nike Windrunner — 1,200,000 VNĐ — Polyester — Màu: Đen — Size: M,L,XL

3.Áo khoác Adidas Essentials — 950,000 VNĐ — Nỉ — Màu: Xám — Size: S,M,L,XL

4.Áo khoác Uniqlo Ultra Light — 650,000 VNĐ — Ultra light down — Màu: Xanh pastel — Size: S,M,L

Đầm/Váy (4 sản phẩm)

1.Đầm body Uniqlo — 550,000 VNĐ — Vải tổng hợp — Màu: Đỏ — Size: S,M,L

2.Váy liền Zara — 750,000 VNĐ — Vải voan — Màu: Hoa — Size: S,M

3.Đầm dạ hội Gucci — 850,000 VNĐ — Lụa — Màu: Đen — Size: S,M

4.Váy công sở H&M — 450,000 VNĐ — Vải Kate — Màu: Xanh dương — Size: S,M,L

Áo Sơ Mi (3 sản phẩm)

1.Áo sơ mi trắng Zara — 550,000 VNĐ — Cotton — Màu: Trắng — Size: S,M,L,XL

2.Áo sơ mi kẻ sọc H&M — 480,000 VNĐ — Cotton — Màu: Xanh trắng — Size: M,L,XL

3.Áo sơ mi Uniqlo Premium — 650,000 VNĐ — Cotton premium — Màu: Xanh pastel — Size: S,M,L

Quần Short (3 sản phẩm)

1.Quần short Nike Sport — 350,000 VNĐ — Polyester — Màu: Đen — Size: M,L,XL

2.Quần short Adidas Originals — 320,000 VNĐ — Cotton — Màu: Xám — Size: S,M,L

3.Quần short Puma Basic — 280,000 VNĐ — Cotton — Màu: Navy — Size: S,M,L,XL

Áo Len / Áo Nỉ (3 sản phẩm)

1.Áo len Gucci — 1,500,000 VNĐ — Vải thun cotton — Màu: Đen — Size: M,L,XL

2.Áo nỉ H&M — 399,000 VNĐ — Cotton, Polyester — Màu: Xanh Navy — Size: XS,S,M,L

3.Áo len Zara — 1,280,000 VNĐ — Cotton, Polyester — Màu: Navy Blue — Size: S,M,L,XL

Tổng cộng: 28 sản phẩm

7 danh mục chính

7 thương hiệu (Nike, Adidas, Zara, Uniqlo, H&M, Gucci, Puma)

Mức giá dao động từ 250,000 VNĐ → 1,500,000 VNĐ

D. Cách tôi có thể giúp
Bạn có thể hỏi tôi các câu hỏi về dự án hoặc sản phẩm, ví dụ:
- "Shop của bạn có bán áo khoác Nike không?"
- "Bạn có sản phẩm nào của Zara không?"
- "Giá của áo thun Gucci Logo là bao nhiêu?"
- "Website này là gì?"
`;

document
  .querySelector(".inputarea button")
  .addEventListener("click", sendMessage);
const conversations = [];
function sendMessage() {
  const userMessage = document.querySelector(".inputarea input").value;
  //neu co nhap du lieu thi moi dua du lieu len vung .chat
  if (userMessage.length) {
    //xoa du lieu trong input
    document.querySelector(".inputarea input").value = "";
    document.querySelector(".chatwindow .chat").insertAdjacentHTML(
      "beforeend",
      `
        <div class="user">
          <p>${userMessage}</p>
        </div>`
    );
    //them vao conversations
    conversations.push({
      role: "user",
      parts: [
        {
          text: userMessage,
        },
      ],
    });

    //tao ra vung trong de hien thi du lieu tra ve
    document.querySelector(".chatwindow .chat").insertAdjacentHTML(
      "beforeend",
      `
          <div class="model">
            <p></p>
          </div>`
    );
    //goi du lieu len model va ket qua tra ve
    goiDuLieu();
  }

  async function goiDuLieu() {
    console.log(conversations);

    const response = await fetch(
      // "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" +
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse&key=" +
      Gemini_KEY,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          system_instruction: {
            parts: [
              {
                text: thongtinHuanluyen,
              },
            ],
          },
          contents: conversations,
        }),
      }
    );
    const models = document.querySelectorAll(".chat .model");

    //xu ly tung doan ket qua tra ve

    const reader = response.body
      .pipeThrough(new TextDecoderStream("utf-8"))
      .getReader();
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      console.log(value);
      //tach theo chu "data:" ra mang
      const arr = value.split("data: ");
      arr.forEach((item, idx) => {
        if (idx > 0 && item.trim().length > 0) {
          try {
            console.log("Chuỗi JSON nhận được:", item);
            // Phân tích (parse) chuỗi JSON thành một đối tượng JavaScript.
            const parsedItem = JSON.parse(item);
            console.log("Đối tượng JSON đã parse:", parsedItem);
            const lastModelP = models[models.length - 1].querySelector("p");
            // --- TRÍCH XUẤT VÀ XỬ LÝ TEXT ---
            // Kiểm tra cấu trúc JSON và lấy phần text trả lời từ AI.
            if (parsedItem.candidates && parsedItem.candidates[0]?.content?.parts?.[0]?.text) {
              const textChunk = parsedItem.candidates[0].content.parts[0].text;
              let processedChunk = textChunk
                .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
                .replace(/\n\* /g, '<br>• ')
                .replace(/\n- /g, '<br>• ')
                .replace(/\n/g, '<br>');

              lastModelP.innerHTML += processedChunk;

            } else {
              console.warn("Chunk không có text hoặc cấu trúc không mong đợi:", parsedItem);
            }
          } catch (e) {
            console.error("Lỗi parse JSON chunk:", e, item);
          }
        }
      });
    }
  }
}