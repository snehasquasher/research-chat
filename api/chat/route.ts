import { Configuration, OpenAIApi } from "openai-edge";
import { Message, OpenAIStream, StreamingTextResponse } from "ai";

const config = new Configuration({
    apiKey: process.env.OPENAI_API_KEY,
});
  
const openai = new OpenAIApi(config);
export const runtime = "edge";

export async function POST(req: Request) {
    try {
        const { messages } = await req.json();

        const prompt = [
            {
                role: "system",
                content: `AI assistant is a brand new, powerful, human-like artificial intelligence.
                    The traits of AI include expert knowledge, helpfulness, cleverness, and articulateness.
                    AI is a well-behaved and well-mannered individual.
                    AI is always friendly, kind, and inspiring, and he is eager to provide vivid and thoughtful responses to the user.
                    AI has the sum of all knowledge in their brain, and is able to accurately answer nearly any question about any topic in conversation.
                    `,
            },
        ];

        // Ask OpenAI for a streaming chat completion given the prompt
        const response = await openai.createChatCompletion({
        model: "gpt-3.5-turbo",
        stream: true,
        messages: [
            ...prompt,
            ...messages.filter((message: Message) => message.role === "user"),
        ],
        });

        const stream = OpenAIStream(response);
        return new StreamingTextResponse(stream);

    } catch (e) {
        throw e;
    }
}
