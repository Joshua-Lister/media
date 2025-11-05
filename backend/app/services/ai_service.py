"""
AI service for article generation and improvement.

**IMPORTANT: UPDATE API KEYS**
Before using this service, update your .env file with:
- OPENAI_API_KEY=your-openai-api-key
OR
- ANTHROPIC_API_KEY=your-anthropic-api-key
"""
from typing import Optional, Dict, List
from app.core.config import settings

# Check which AI provider is configured
HAS_OPENAI = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-your-openai-api-key")
HAS_ANTHROPIC = bool(settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "sk-ant-your-anthropic-api-key")

if HAS_OPENAI:
    from openai import AsyncOpenAI
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

if HAS_ANTHROPIC:
    from anthropic import AsyncAnthropic
    anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


class AIService:
    """Service for AI-powered article operations."""

    @staticmethod
    async def generate_article(
        topic: str,
        keywords: Optional[List[str]] = None,
        tone: str = "informative",
        length: str = "medium",
    ) -> Dict[str, str]:
        """
        Generate an article using AI.

        **REQUIRES: OpenAI or Anthropic API key configured in .env**

        Args:
            topic: Article topic
            keywords: Optional keywords to include
            tone: Writing tone (informative, casual, formal, etc.)
            length: Article length (short, medium, long)

        Returns:
            Dict containing title, content, and summary

        Raises:
            ValueError: If no AI provider is configured
        """
        if not HAS_OPENAI and not HAS_ANTHROPIC:
            raise ValueError(
                "No AI provider configured. Please set OPENAI_API_KEY or "
                "ANTHROPIC_API_KEY in your .env file"
            )

        # Define length targets
        length_map = {
            "short": "500-800 words",
            "medium": "1000-1500 words",
            "long": "2000-3000 words",
        }
        target_length = length_map.get(length, "1000-1500 words")

        # Build prompt
        prompt = f"""Write a comprehensive, well-researched article about: {topic}

Tone: {tone}
Length: {target_length}
"""
        if keywords:
            prompt += f"\nInclude these keywords: {', '.join(keywords)}\n"

        prompt += """
Structure the article with:
1. A compelling headline
2. An engaging introduction
3. Well-organized body sections with subheadings
4. A thoughtful conclusion
5. Cite credible sources where appropriate

Please provide the response in this format:
TITLE: [Your title here]
SUMMARY: [2-3 sentence summary]
CONTENT: [Full article content with markdown formatting]
"""

        # Use OpenAI if available, otherwise Anthropic
        if HAS_OPENAI:
            response = await openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert journalist who writes clear, engaging, and well-researched articles.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            content = response.choices[0].message.content
        elif HAS_ANTHROPIC:
            response = await anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text
        else:
            raise ValueError("No AI provider available")

        # Parse response
        return AIService._parse_article_response(content)

    @staticmethod
    async def improve_draft(
        title: str, content: str, feedback: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Improve an article draft using AI.

        **REQUIRES: OpenAI or Anthropic API key configured in .env**

        Args:
            title: Article title
            content: Article content
            feedback: Optional specific feedback

        Returns:
            Dict containing improved title and content
        """
        if not HAS_OPENAI and not HAS_ANTHROPIC:
            raise ValueError(
                "No AI provider configured. Please set OPENAI_API_KEY or "
                "ANTHROPIC_API_KEY in your .env file"
            )

        prompt = f"""Please improve this article draft:

TITLE: {title}

CONTENT:
{content}
"""
        if feedback:
            prompt += f"\n\nSpecific feedback to address:\n{feedback}\n"

        prompt += """
Improve the article by:
1. Enhancing clarity and readability
2. Strengthening arguments and evidence
3. Improving flow and transitions
4. Fixing grammar and style issues
5. Making the writing more engaging

Provide the improved version in this format:
TITLE: [Improved title]
CONTENT: [Improved content]
"""

        if HAS_OPENAI:
            response = await openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert editor who helps improve articles.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
            )
            content = response.choices[0].message.content
        else:
            response = await anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text

        # Parse response
        lines = content.split("\n")
        improved_title = title
        improved_content = content

        for i, line in enumerate(lines):
            if line.startswith("TITLE:"):
                improved_title = line.replace("TITLE:", "").strip()
            elif line.startswith("CONTENT:"):
                improved_content = "\n".join(lines[i + 1 :]).strip()
                break

        return {"title": improved_title, "content": improved_content}

    @staticmethod
    async def generate_summary(content: str, max_sentences: int = 3) -> str:
        """
        Generate a summary of article content.

        **REQUIRES: OpenAI or Anthropic API key configured in .env**

        Args:
            content: Article content
            max_sentences: Maximum number of sentences in summary

        Returns:
            str: Article summary
        """
        if not HAS_OPENAI and not HAS_ANTHROPIC:
            # Fallback: simple extraction of first few sentences
            sentences = content.split(". ")
            return ". ".join(sentences[:max_sentences]) + "."

        prompt = f"""Summarize the following article in {max_sentences} clear, concise sentences:

{content}
"""

        if HAS_OPENAI:
            response = await openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        else:
            response = await anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()

    @staticmethod
    async def fact_check(content: str) -> Dict[str, any]:
        """
        Perform basic fact-checking on article content.

        **REQUIRES: OpenAI or Anthropic API key configured in .env**

        Args:
            content: Article content to fact-check

        Returns:
            Dict with fact-check results and suggestions
        """
        if not HAS_OPENAI and not HAS_ANTHROPIC:
            return {
                "checked": False,
                "message": "AI provider not configured for fact-checking",
            }

        prompt = f"""Analyze the following article for potential factual issues:

{content}

Identify:
1. Claims that need sources or verification
2. Potential factual inaccuracies
3. Statements that are overly broad or misleading
4. Missing context or nuance

Provide a brief report on the article's factual reliability.
"""

        if HAS_OPENAI:
            response = await openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000,
            )
            analysis = response.choices[0].message.content
        else:
            response = await anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            analysis = response.content[0].text

        return {"checked": True, "analysis": analysis}

    @staticmethod
    def _parse_article_response(response: str) -> Dict[str, str]:
        """Parse AI response into structured article data."""
        lines = response.split("\n")
        title = ""
        summary = ""
        content = ""
        current_section = None

        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                current_section = "title"
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
                current_section = "summary"
            elif line.startswith("CONTENT:"):
                current_section = "content"
            elif current_section == "content":
                content += line + "\n"
            elif current_section == "summary" and summary and not line.startswith(
                "CONTENT:"
            ):
                summary += " " + line.strip()

        return {
            "title": title.strip(),
            "summary": summary.strip(),
            "content": content.strip(),
        }
