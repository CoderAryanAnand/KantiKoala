"""
Citation Generator API routes.

This module provides endpoints for managing citation groups and citations.
"""
from flask import Blueprint, request, jsonify
import json
import re

from ..models import CitationGroup, Citation
from ..utils import login_required, csrf_protect
from ..extensions import db, limiter

# Define the blueprint for citation-related API routes
citations_bp = Blueprint(
    "citations", __name__, template_folder="../templates", static_folder="../static"
)

# Apply rate limit to all citation API routes (60 requests per minute)
@citations_bp.before_request
@limiter.limit("60 per minute")
def limit_citations_api():
    pass


def clean_citation(citation: str) -> str:
    """
    Clean up a citation string by removing empty fields and fixing formatting.
    
    Args:
        citation: Raw citation string that may have empty fields
        
    Returns:
        Cleaned citation string
    """
    # Remove empty parentheses: (), (n.d.), ( ), (.)
    citation = re.sub(r'\s*\(\s*\)', '', citation)
    citation = re.sub(r'\s*\(n\.d\.\)', '', citation)
    citation = re.sub(r'\s*\(\s*\.\s*\)', '', citation)
    
    # Remove empty brackets: [], [ ]
    citation = re.sub(r'\s*\[\s*\]', '', citation)
    citation = re.sub(r'\s*\[\s*,\s*\]', '', citation)
    
    # Remove patterns like ", ," or ", ." or ". ," 
    citation = re.sub(r',\s*,', ',', citation)
    citation = re.sub(r',\s*\.', '.', citation)
    citation = re.sub(r'\.\s*,', '.', citation)
    
    # Remove patterns like ": ." or ": ,"
    citation = re.sub(r':\s*\.', '.', citation)
    citation = re.sub(r':\s*,', ',', citation)
    
    # Remove standalone periods or commas after other punctuation
    citation = re.sub(r'\.\s*\.', '.', citation)
    
    # Remove leading/trailing commas, colons, semicolons in segments
    citation = re.sub(r'\.\s*,\s*\.', '.', citation)
    
    # Remove "In ." or "In ," patterns
    citation = re.sub(r'In\s*<i>\s*</i>', '', citation)
    citation = re.sub(r'In\s*\.', '.', citation)
    citation = re.sub(r'In\s*,', ',', citation)
    
    # Remove empty italic tags
    citation = re.sub(r'<i>\s*</i>', '', citation)
    citation = re.sub(r'<i>\s*:\s*</i>', '', citation)
    
    # Remove "Abgerufen am , von" or "Accessed ." patterns when no date/url
    citation = re.sub(r'Abgerufen am\s*,\s*von\s*$', '', citation)
    citation = re.sub(r'Abgerufen am\s*,\s*von\s*\.?$', '', citation)
    citation = re.sub(r'Accessed\s*\.$', '', citation)
    
    # Clean up multiple spaces
    citation = re.sub(r'\s+', ' ', citation)
    
    # Clean up space before punctuation
    citation = re.sub(r'\s+\.', '.', citation)
    citation = re.sub(r'\s+,', ',', citation)
    
    # Clean up patterns like ". ." or ",."
    citation = re.sub(r'\.\s*\.', '.', citation)
    citation = re.sub(r',\.', '.', citation)
    
    # Remove trailing/leading whitespace
    citation = citation.strip()
    
    # Remove trailing comma or colon
    citation = re.sub(r'[,:]$', '.', citation)
    
    # Ensure it ends with a period if it has content
    if citation and not citation.endswith('.') and not citation.endswith('?') and not citation.endswith('!'):
        citation += '.'
    
    # Fix double periods
    citation = re.sub(r'\.\.+', '.', citation)
    
    return citation


# -------------------------------
# Citation formatting functions
# -------------------------------

def format_apa(source_type: str, data: dict) -> str:
    """Format a citation in APA style (7th edition)."""
    
    # Helper for title with subtitle
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    full_title = f"{title}: {subtitle}" if subtitle else title
    
    if source_type == "book":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        publisher = data.get("publisher", "")
        return f"{authors} ({year}). <i>{full_title}</i>. {publisher}."
    
    elif source_type == "anthology":
        editors = data.get("editors", "")
        year = data.get("year", "n.d.")
        publisher = data.get("publisher", "")
        return f"{editors} (Eds.). ({year}). <i>{full_title}</i>. {publisher}."
    
    elif source_type == "anthology_chapter":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        editors = data.get("editors", "")
        container_title = data.get("container_title", "")
        publisher = data.get("publisher", "")
        pages = data.get("pages", "")
        pages_part = f" (pp. {pages})" if pages else ""
        return f"{authors} ({year}). {full_title}. In {editors} (Eds.), <i>{container_title}</i>{pages_part}. {publisher}."
    
    elif source_type == "thesis":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        thesis_type = data.get("thesis_type", "")
        university = data.get("university", "")
        return f"{authors} ({year}). <i>{full_title}</i> [{thesis_type}, {university}]."
    
    elif source_type == "newspaper_article":
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        newspaper = data.get("newspaper", "")
        pages = data.get("pages", "")
        pages_part = f", {pages}" if pages else ""
        return f"{authors} ({date}). {full_title}. <i>{newspaper}</i>{pages_part}."
    
    elif source_type == "journal_article":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        pages = data.get("pages", "")
        issue_part = f"({issue})" if issue else ""
        pages_part = f", {pages}" if pages else ""
        return f"{authors} ({year}). {full_title}. <i>{journal}</i>, {volume}{issue_part}{pages_part}."
    
    elif source_type == "website":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        site_name = data.get("site_name", data.get("siteName", ""))
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors} " if authors else ""
        return f"{author_part}({year}). {full_title}. <i>{site_name}</i>. Abgerufen am {access_date}, von {url}"
    
    elif source_type == "online_media_article":
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        publication = data.get("publication", "")
        url = data.get("url", "")
        return f"{authors} ({date}). {full_title}. <i>{publication}</i>. {url}"
    
    elif source_type == "ebook":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        publisher = data.get("publisher", "")
        identifier = data.get("identifier", "")
        id_part = f" {identifier}" if identifier else ""
        return f"{authors} ({year}). <i>{full_title}</i>. {publisher}.{id_part}"
    
    elif source_type == "blog":
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        blog_name = data.get("blog_name", "")
        url = data.get("url", "")
        return f"{authors} ({date}). {full_title}. <i>{blog_name}</i>. {url}"
    
    elif source_type == "social_media":
        authors = data.get("authors", "")
        handle = data.get("handle", "")
        date = data.get("date", "n.d.")
        platform = data.get("platform", "")
        url = data.get("url", "")
        handle_part = f" [{handle}]" if handle else ""
        return f"{authors}{handle_part}. ({date}). {full_title} [{platform}]. {url}"
    
    elif source_type == "online_lexicon":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        lexicon = data.get("lexicon", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors} " if authors else ""
        return f"{author_part}({year}). {full_title}. In <i>{lexicon}</i>. Abgerufen am {access_date}, von {url}"
    
    elif source_type == "ai":
        ai_name = data.get("ai_name", "")
        version = data.get("version", "")
        date = data.get("date", "n.d.")
        prompt = data.get("prompt", "")
        return f"{ai_name}. ({date}). Response to \"{prompt}\" [{version}]."
    
    elif source_type == "image_web":
        number = data.get("number", "")
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        url = data.get("url", "")
        num_part = f"Abb. {number}: " if number else ""
        return f"{num_part}{authors}. ({date}). <i>{full_title}</i>. {url}"
    
    elif source_type == "podcast":
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        podcast_name = data.get("podcast_name", "")
        url = data.get("url", "")
        return f"{authors} (Host). ({date}). {full_title} [Audio podcast episode]. In <i>{podcast_name}</i>. {url}"
    
    elif source_type == "song":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        album = data.get("album", "")
        label = data.get("label", "")
        return f"{authors} ({year}). {full_title} [Song]. On <i>{album}</i>. {label}."
    
    elif source_type == "film":
        directors = data.get("directors", "")
        year = data.get("year", "n.d.")
        distributor = data.get("distributor", "")
        return f"{directors} (Director). ({year}). <i>{full_title}</i> [Film]. {distributor}."
    
    elif source_type == "tv_episode":
        authors = data.get("authors", "")
        date = data.get("date", "n.d.")
        show = data.get("show", "")
        broadcaster = data.get("broadcaster", "")
        return f"{authors} ({date}). {full_title} [TV series episode]. In <i>{show}</i>. {broadcaster}."
    
    elif source_type == "streaming_series":
        episode_title = data.get("episode_title", "")
        credits = data.get("credits", "")
        series = data.get("series", "")
        season = data.get("season", "")
        episode_num = data.get("episode_num", "")
        year = data.get("year", "n.d.")
        platform = data.get("platform", "")
        return f"{credits} ({year}). {episode_title} (Season {season}, Episode {episode_num}) [TV series episode]. In <i>{series}</i>. {platform}."
    
    elif source_type == "video_stream":
        username = data.get("username", "")
        date = data.get("date", "n.d.")
        url = data.get("url", "")
        return f"{username}. ({date}). <i>{full_title}</i> [Video]. {url}"
    
    elif source_type == "game":
        company = data.get("company", "")
        year = data.get("year", "n.d.")
        platform = data.get("platform", "")
        return f"{company}. ({year}). <i>{full_title}</i> [Video game]. {platform}."
    
    elif source_type == "interview":
        interviewer = data.get("interviewer", "")
        interviewee = data.get("interviewee", "")
        date = data.get("date", "n.d.")
        return f"{interviewer} (Interviewer) & {interviewee} (Interviewee). ({date}). [Interview]."
    
    # Legacy support for "article" type
    elif source_type == "article":
        authors = data.get("authors", "")
        year = data.get("year", "n.d.")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        pages = data.get("pages", "")
        issue_part = f"({issue})" if issue else ""
        pages_part = f", {pages}" if pages else ""
        return f"{authors} ({year}). {full_title}. <i>{journal}</i>, {volume}{issue_part}{pages_part}."
    
    return f"[Unbekannter Quellentyp: {source_type}]"


def format_mla(source_type: str, data: dict) -> str:
    """Format a citation in MLA style (9th edition)."""
    
    # Helper for title with subtitle
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    full_title = f"{title}: {subtitle}" if subtitle else title
    
    if source_type == "book":
        authors = data.get("authors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        return f"{authors}. <i>{full_title}</i>. {publisher}, {year}."
    
    elif source_type == "anthology":
        editors = data.get("editors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        return f"{editors}, editors. <i>{full_title}</i>. {publisher}, {year}."
    
    elif source_type == "anthology_chapter":
        authors = data.get("authors", "")
        editors = data.get("editors", "")
        container_title = data.get("container_title", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        return f'{authors}. "{full_title}." <i>{container_title}</i>, edited by {editors}, {publisher}, {year}, pp. {pages}.'
    
    elif source_type == "thesis":
        authors = data.get("authors", "")
        year = data.get("year", "")
        thesis_type = data.get("thesis_type", "")
        university = data.get("university", "")
        return f"{authors}. <i>{full_title}</i>. {year}. {university}, {thesis_type}."
    
    elif source_type == "newspaper_article":
        authors = data.get("authors", "")
        newspaper = data.get("newspaper", "")
        date = data.get("date", "")
        pages = data.get("pages", "")
        pages_part = f", pp. {pages}" if pages else ""
        return f'{authors}. "{full_title}." <i>{newspaper}</i>, {date}{pages_part}.'
    
    elif source_type == "journal_article":
        authors = data.get("authors", "")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        vol_issue = f"vol. {volume}, no. {issue}, " if volume and issue else ""
        pages_part = f"pp. {pages}" if pages else ""
        return f'{authors}. "{full_title}." <i>{journal}</i>, {vol_issue}{year}, {pages_part}.'
    
    elif source_type == "website":
        authors = data.get("authors", "")
        site_name = data.get("site_name", data.get("siteName", ""))
        year = data.get("year", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors}. " if authors else ""
        return f'{author_part}"{full_title}." <i>{site_name}</i>, {year}, {url}. Accessed {access_date}.'
    
    elif source_type == "online_media_article":
        authors = data.get("authors", "")
        publication = data.get("publication", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}. "{full_title}." <i>{publication}</i>, {date}, {url}.'
    
    elif source_type == "ebook":
        authors = data.get("authors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        identifier = data.get("identifier", "")
        id_part = f" {identifier}." if identifier else ""
        return f"{authors}. <i>{full_title}</i>. E-book, {publisher}, {year}.{id_part}"
    
    elif source_type == "blog":
        authors = data.get("authors", "")
        blog_name = data.get("blog_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}. "{full_title}." <i>{blog_name}</i>, {date}, {url}.'
    
    elif source_type == "social_media":
        authors = data.get("authors", "")
        handle = data.get("handle", "")
        platform = data.get("platform", "")
        date = data.get("date", "")
        url = data.get("url", "")
        handle_part = f" ({handle})" if handle else ""
        return f'{authors}{handle_part}. "{full_title}." <i>{platform}</i>, {date}, {url}.'
    
    elif source_type == "online_lexicon":
        authors = data.get("authors", "")
        lexicon = data.get("lexicon", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors}. " if authors else ""
        return f'{author_part}"{full_title}." <i>{lexicon}</i>, {url}. Accessed {access_date}.'
    
    elif source_type == "ai":
        ai_name = data.get("ai_name", "")
        version = data.get("version", "")
        prompt = data.get("prompt", "")
        date = data.get("date", "")
        return f'"{prompt}" prompt. <i>{ai_name}</i>, {version}, {date}.'
    
    elif source_type == "image_web":
        number = data.get("number", "")
        authors = data.get("authors", "")
        date = data.get("date", "")
        url = data.get("url", "")
        num_part = f"Fig. {number}: " if number else ""
        return f'{num_part}{authors}. <i>{full_title}</i>. {date}, {url}.'
    
    elif source_type == "podcast":
        authors = data.get("authors", "")
        podcast_name = data.get("podcast_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}, host. "{full_title}." <i>{podcast_name}</i>, {date}, {url}.'
    
    elif source_type == "song":
        authors = data.get("authors", "")
        album = data.get("album", "")
        label = data.get("label", "")
        year = data.get("year", "")
        return f'{authors}. "{full_title}." <i>{album}</i>, {label}, {year}.'
    
    elif source_type == "film":
        directors = data.get("directors", "")
        distributor = data.get("distributor", "")
        year = data.get("year", "")
        return f"<i>{full_title}</i>. Directed by {directors}, {distributor}, {year}."
    
    elif source_type == "tv_episode":
        authors = data.get("authors", "")
        show = data.get("show", "")
        broadcaster = data.get("broadcaster", "")
        date = data.get("date", "")
        return f'"{full_title}." <i>{show}</i>, {broadcaster}, {date}.'
    
    elif source_type == "streaming_series":
        episode_title = data.get("episode_title", "")
        series = data.get("series", "")
        season = data.get("season", "")
        episode_num = data.get("episode_num", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        return f'"{episode_title}." <i>{series}</i>, season {season}, episode {episode_num}, {platform}, {year}.'
    
    elif source_type == "video_stream":
        username = data.get("username", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{username}. "{full_title}." Online video, {date}, {url}.'
    
    elif source_type == "game":
        company = data.get("company", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        return f"<i>{full_title}</i>. {company}, {platform}, {year}."
    
    elif source_type == "interview":
        interviewer = data.get("interviewer", "")
        interviewee = data.get("interviewee", "")
        date = data.get("date", "")
        place = data.get("place", "")
        return f"{interviewee}. Interview by {interviewer}. {date}."
    
    # Legacy support for "article" type
    elif source_type == "article":
        authors = data.get("authors", "")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        vol_issue = f"vol. {volume}, no. {issue}, " if volume and issue else ""
        pages_part = f"pp. {pages}" if pages else ""
        return f'{authors}. "{full_title}." <i>{journal}</i>, {vol_issue}{year}, {pages_part}.'
    
    return f"[Unbekannter Quellentyp: {source_type}]"


def format_chicago(source_type: str, data: dict) -> str:
    """Format a citation in Chicago style (17th edition, bibliography format)."""
    
    # Helper for title with subtitle
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    full_title = f"{title}: {subtitle}" if subtitle else title
    
    if source_type == "book":
        authors = data.get("authors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        location = data.get("location", data.get("place", ""))
        loc_part = f"{location}: " if location else ""
        return f"{authors}. <i>{full_title}</i>. {loc_part}{publisher}, {year}."
    
    elif source_type == "anthology":
        editors = data.get("editors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        location = data.get("location", data.get("place", ""))
        loc_part = f"{location}: " if location else ""
        return f"{editors}, eds. <i>{full_title}</i>. {loc_part}{publisher}, {year}."
    
    elif source_type == "anthology_chapter":
        authors = data.get("authors", "")
        editors = data.get("editors", "")
        container_title = data.get("container_title", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        location = data.get("location", data.get("place", ""))
        pages = data.get("pages", "")
        loc_part = f"{location}: " if location else ""
        return f'{authors}. "{full_title}." In <i>{container_title}</i>, edited by {editors}, {pages}. {loc_part}{publisher}, {year}.'
    
    elif source_type == "thesis":
        authors = data.get("authors", "")
        year = data.get("year", "")
        thesis_type = data.get("thesis_type", "")
        university = data.get("university", "")
        return f'{authors}. "{full_title}." {thesis_type}, {university}, {year}.'
    
    elif source_type == "newspaper_article":
        authors = data.get("authors", "")
        newspaper = data.get("newspaper", "")
        date = data.get("date", "")
        return f'{authors}. "{full_title}." <i>{newspaper}</i>, {date}.'
    
    elif source_type == "journal_article":
        authors = data.get("authors", "")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        issue_part = f", no. {issue}" if issue else ""
        return f'{authors}. "{full_title}." <i>{journal}</i> {volume}{issue_part} ({year}): {pages}.'
    
    elif source_type == "website":
        authors = data.get("authors", "")
        site_name = data.get("site_name", data.get("siteName", ""))
        year = data.get("year", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors}. " if authors else ""
        return f'{author_part}"{full_title}." {site_name}. {year}. {url} (accessed {access_date}).'
    
    elif source_type == "online_media_article":
        authors = data.get("authors", "")
        publication = data.get("publication", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}. "{full_title}." <i>{publication}</i>, {date}. {url}.'
    
    elif source_type == "ebook":
        authors = data.get("authors", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        location = data.get("location", data.get("place", ""))
        identifier = data.get("identifier", "")
        loc_part = f"{location}: " if location else ""
        id_part = f" {identifier}." if identifier else ""
        return f"{authors}. <i>{full_title}</i>. {loc_part}{publisher}, {year}. E-book.{id_part}"
    
    elif source_type == "blog":
        authors = data.get("authors", "")
        blog_name = data.get("blog_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}. "{full_title}." {blog_name} (blog), {date}. {url}.'
    
    elif source_type == "social_media":
        authors = data.get("authors", "")
        handle = data.get("handle", "")
        platform = data.get("platform", "")
        date = data.get("date", "")
        url = data.get("url", "")
        handle_part = f" ({handle})" if handle else ""
        return f'{authors}{handle_part}. "{full_title}." {platform}, {date}. {url}.'
    
    elif source_type == "online_lexicon":
        authors = data.get("authors", "")
        lexicon = data.get("lexicon", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        author_part = f"{authors}. " if authors else ""
        return f'{author_part}"{full_title}." <i>{lexicon}</i>. Accessed {access_date}. {url}.'
    
    elif source_type == "ai":
        ai_name = data.get("ai_name", "")
        version = data.get("version", "")
        prompt = data.get("prompt", "")
        date = data.get("date", "")
        return f'{ai_name}. "{prompt}." {version}. {date}.'
    
    elif source_type == "image_web":
        number = data.get("number", "")
        authors = data.get("authors", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", data.get("accessDate", ""))
        num_part = f"Fig. {number}. " if number else ""
        return f'{num_part}{authors}. <i>{full_title}</i>. {date}. {url}.'
    
    elif source_type == "podcast":
        authors = data.get("authors", "")
        podcast_name = data.get("podcast_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{authors}. "{full_title}." In <i>{podcast_name}</i>. Podcast audio. {date}. {url}.'
    
    elif source_type == "song":
        authors = data.get("authors", "")
        album = data.get("album", "")
        label = data.get("label", "")
        year = data.get("year", "")
        return f'{authors}. "{full_title}." Track on <i>{album}</i>. {label}, {year}.'
    
    elif source_type == "film":
        directors = data.get("directors", "")
        distributor = data.get("distributor", "")
        country = data.get("country", "")
        year = data.get("year", "")
        country_part = f"{country}: " if country else ""
        return f"<i>{full_title}</i>. Directed by {directors}. {country_part}{distributor}, {year}."
    
    elif source_type == "tv_episode":
        authors = data.get("authors", "")
        show = data.get("show", "")
        broadcaster = data.get("broadcaster", "")
        date = data.get("date", "")
        return f'"{full_title}." <i>{show}</i>. {broadcaster}, {date}.'
    
    elif source_type == "streaming_series":
        episode_title = data.get("episode_title", "")
        credits = data.get("credits", "")
        series = data.get("series", "")
        season = data.get("season", "")
        episode_num = data.get("episode_num", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        return f'"{episode_title}." <i>{series}</i>, season {season}, episode {episode_num}. {credits}. {platform}, {year}.'
    
    elif source_type == "video_stream":
        username = data.get("username", "")
        date = data.get("date", "")
        url = data.get("url", "")
        return f'{username}. "{full_title}." {date}. Video. {url}.'
    
    elif source_type == "game":
        company = data.get("company", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        return f"<i>{full_title}</i>. {company}. {platform}. {year}."
    
    elif source_type == "interview":
        interviewer = data.get("interviewer", "")
        interviewee = data.get("interviewee", "")
        place = data.get("place", "")
        date = data.get("date", "")
        return f"{interviewee}. Interview by {interviewer}. {place}, {date}."
    
    # Legacy support for "article" type
    elif source_type == "article":
        authors = data.get("authors", "")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        issue_part = f", no. {issue}" if issue else ""
        return f'{authors}. "{full_title}." <i>{journal}</i> {volume}{issue_part} ({year}): {pages}.'
    
    return f"[Unbekannter Quellentyp: {source_type}]"

def format_kanti_baden(source_type: str, data: dict) -> str:
    """
    Format a citation for the Kantonsschule Baden Quellenverzeichnis (Bibliography).
    Based on the 2025 guidelines.
    
    Args:
        source_type (str): The type of source (e.g., 'book', 'website', 'ai', 'social_media').
        data (dict): A dictionary containing the bibliographic information.
                     Keys: authors, title, subtitle, year, place, publisher, url, 
                     access_date, date, journal, volume, issue, pages, etc.
    
    Returns:
        str: The formatted citation string.
    """
    
    # Helper to join title and subtitle
    title = data.get("title", "")
    subtitle = data.get("subtitle", "")
    full_title = f"{title}. {subtitle}" if subtitle else title
    
    # --- 2. Gedruckte Publikationen (Printed Publications) ---
    
    if source_type == "book":
        # [cite: 133] Name(n), Vorname(n): Titel. Untertitel, Ort: Verlag, Jahr (ggf. Auflage).
        authors = data.get("authors", "")
        place = data.get("place", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        edition = data.get("edition", "") # Optional
        
        edition_part = f" ({edition})" if edition else ""
        return f"{authors}: {full_title}, {place}: {publisher}, {year}{edition_part}."

    elif source_type == "anthology": # Sammelband
        # [cite: 142] Name(n) (Hg.): Titel. Untertitel, Ort: Verlag, Jahr.
        editors = data.get("editors", "") # Pass names here
        place = data.get("place", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        
        return f"{editors} (Hg.): {full_title}, {place}: {publisher}, {year}."

    elif source_type == "anthology_chapter": # Beitrag in Sammelband
        # [cite: 149] Name: Titel, in: Hg (Hg.): Titel. Ort: Verlag, Jahr, S. x-y.
        authors = data.get("authors", "")
        editors = data.get("editors", "")
        container_title = data.get("container_title", "")
        place = data.get("place", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        
        return f"{authors}: {full_title}, in: {editors} (Hg.): {container_title}. {place}: {publisher}, {year}, S. {pages}."

    elif source_type == "thesis": # Hochschulschrift
        # [cite: 154] Name: Titel. Art. Uni. Ort, Jahr.
        authors = data.get("authors", "")
        thesis_type = data.get("thesis_type", "") # e.g., Bachelorarbeit
        university = data.get("university", "")
        place = data.get("place", "")
        year = data.get("year", "")
        
        return f"{authors}: {full_title}. {thesis_type}. {university}. {place}, {year}."

    elif source_type == "newspaper_article":
        # [cite: 166] Name: Titel. Untertitel, in: Zeitung, Erscheinungsdatum – TT.MM.JJJJ, Seitenangabe.
        authors = data.get("authors", "")
        newspaper = data.get("newspaper", "")
        date = data.get("date", "") # TT.MM.JJJJ
        pages = data.get("pages", "")
        
        return f"{authors}: {full_title}, in: {newspaper}, {date}, S. {pages}."

    elif source_type == "journal_article":
        # [cite: 172] Name: Titel, in: Zeitschrift Band, Nr. (Jahr), S. x-y.
        authors = data.get("authors", "")
        journal = data.get("journal", "")
        volume = data.get("volume", "")
        issue = data.get("issue", "")
        year = data.get("year", "")
        pages = data.get("pages", "")
        
        issue_part = f", Nr. {issue}" if issue else ""
        volume_part = f" {volume}" if volume else ""
        
        return f"{authors}: {full_title}, in: {journal}{volume_part}{issue_part} ({year}), S. {pages}."

    # --- 3. Digitale Publikationen (Digital Publications) ---

    elif source_type == "website":
        # [cite: 184] Name: Titel. Untertitel, Veröffentlichungsdatum – TT.MM.JJJJ. URL, abgerufen am TT.MM.JJJJ.
        authors = data.get("authors", "")
        date = data.get("date", "") # TT.MM.JJJJ
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        if authors:
             return f"{authors}: {full_title}, {date}. {url}, abgerufen am {access_date}."
        else:
            # [cite: 188] No author: Titel des Eintrages, in: Name der Website, Veröffentlichungsdatum – TT.MM.JJJJ. URL, abgerufen am TT.MM.JJJJ.
            site_name = data.get("site_name", "")
            return f"{full_title}, in: {site_name}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "online_media_article":
        # [cite: 191] Name: Titel, in: Publikation, Datum. URL...
        authors = data.get("authors", "")
        publication = data.get("publication", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{authors}: {full_title}, in: {publication}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "ebook":
        # [cite: 198] Name: Titel (E-Book), Ort: Verlag, Jahr. DOI...
        authors = data.get("authors", "")
        place = data.get("place", "")
        publisher = data.get("publisher", "")
        year = data.get("year", "")
        identifier = data.get("identifier", "") # DOI or ISBN
        
        return f"{authors}: {full_title} (E-Book), {place}: {publisher}, {year}. {identifier}."

    elif source_type == "blog":
        # [cite: 206] Name: Artikeltitel, in: Blogname, Datum. URL...
        authors = data.get("authors", "")
        blog_name = data.get("blog_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{authors}: {full_title}, in: {blog_name}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "social_media":
        # [cite: 210] Name [Account]: Titel, Plattform, Datum. URL...
        authors = data.get("authors", "")
        handle = data.get("handle", "") # e.g., @BarackObama
        platform = data.get("platform", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        handle_part = f" [{handle}]" if handle else ""
        return f"{authors}{handle_part}: {full_title}, {platform}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "online_lexicon":
        # [cite: 216] Name: Titel, in: Lexikon, Datum. URL...
        authors = data.get("authors", "")
        lexicon = data.get("lexicon", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{authors}: {full_title}, in: {lexicon}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "ai":
        # [cite: 222] KI (Version): «Prompt», Datum. Art der Übernahme.
        ai_name = data.get("ai_name", "") # e.g., ChatGPT
        version = data.get("version", "")
        prompt = data.get("prompt", "")
        date = data.get("date", "")
        usage_type = data.get("usage_type", "") # e.g., Als Inspiration verwendet
        
        return f"{ai_name} ({version}): «{prompt}», {date}. {usage_type}."

    # --- 4. Abbildungen (Images) ---
    
    elif source_type == "image_web":
        # [cite: 265] Abb. X: Name: Titel, Datum. URL...
        number = data.get("number", "")
        authors = data.get("authors", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"Abb. {number}: {authors}: {full_title}, {date}. {url}, abgerufen am {access_date}."
    
    # --- 5 & 6. Audio / Audiovisuelle Quellen ---

    elif source_type == "podcast":
        # [cite: 280] Name: Titel, in: Podcast. Datum. URL...
        authors = data.get("authors", "")
        podcast_name = data.get("podcast_name", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{authors}: {full_title}, in: {podcast_name}. {date}. {url}, abgerufen am {access_date}."

    elif source_type == "song":
        # [cite: 285] Name: Songtitel. Album. Label, Jahr.
        authors = data.get("authors", "")
        album = data.get("album", "")
        label = data.get("label", "")
        year = data.get("year", "")
        
        return f"{authors}: {full_title}. {album}. {label}, {year}."

    elif source_type == "film":
        # [cite: 292] Regisseur: Titel. Anbieter, Land, Jahr.
        directors = data.get("directors", "")
        distributor = data.get("distributor", "") # Anbieter/Studio
        country = data.get("country", "")
        year = data.get("year", "")
        
        return f"{directors}: {full_title}. {distributor}, {country}, {year}."

    elif source_type == "tv_episode":
        # [cite: 294] Name: Titel, in: Sendung. Sender, Datum. URL...
        authors = data.get("authors", "")
        show = data.get("show", "")
        broadcaster = data.get("broadcaster", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{authors}: {full_title}, in: {show}. {broadcaster}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "streaming_series":
        # [cite: 299] «Folge». Drehbuch: X, Prod: Y. Serie, Staffel, Folge, Plattform Jahr...
        episode_title = data.get("episode_title", "")
        credits = data.get("credits", "") # e.g. "Drehbuch: X, Produzentin: Y"
        series = data.get("series", "")
        season = data.get("season", "")
        episode_num = data.get("episode_num", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        access_date = data.get("access_date", "")
        
        return f"«{episode_title}». {credits}. {series}, Staffel {season}, Folge {episode_num}, {platform} {year}, abgerufen am {access_date}."

    elif source_type == "video_stream":
        # [cite: 303] User: Titel, Datum. URL...
        username = data.get("username", "")
        date = data.get("date", "")
        url = data.get("url", "")
        access_date = data.get("access_date", "")
        
        return f"{username}: {full_title}, {date}. {url}, abgerufen am {access_date}."

    elif source_type == "game":
        # [cite: 309] Titel. Firma. (Plattform) Jahr.
        company = data.get("company", "")
        platform = data.get("platform", "")
        year = data.get("year", "")
        
        return f"{full_title}. {company}. ({platform}) {year}."

    elif source_type == "interview":
        # [cite: 318] Interviewer: Interview mit X, Ort, Datum.
        interviewer = data.get("interviewer", "")
        interviewee = data.get("interviewee", "")
        place = data.get("place", "")
        date = data.get("date", "")
        
        return f"{interviewer}: Interview mit {interviewee}, {place}, {date}."

    return f"[Unbekannter Quellentyp: {source_type}]"


def format_citation(style: str, source_type: str, data: dict) -> str:
    """
    Format a citation based on the specified style.
    
    Args:
        style: Citation style (apa, mla, chicago, kanti_baden)
        source_type: Type of source (book, website, article, etc.)
        data: Dictionary with source information
        
    Returns:
        Formatted citation string
    """
    formatters = {
        "apa": format_apa,
        "mla": format_mla,
        "chicago": format_chicago,
        "kanti_baden": format_kanti_baden,
    }
    
    formatter = formatters.get(style.lower())
    if not formatter:
        return f"[Unbekannter Zitierstil: {style}]"
    
    # Format and clean the citation
    raw_citation = formatter(source_type, data)
    return clean_citation(raw_citation)


# -------------------------------
# Citation Group API routes
# -------------------------------

@citations_bp.route("/groups", methods=["GET"])
@login_required
def get_groups(user):
    """
    Get all citation groups for the current user.
    
    Returns:
        JSON: List of groups with their citations.
    """
    groups = CitationGroup.query.filter_by(user_id=user.id).all()
    
    result = []
    for group in groups:
        citations = []
        for citation in group.citations:
            citations.append({
                "id": citation.id,
                "sourceType": citation.source_type,
                "style": citation.style,
                "data": json.loads(citation.data),
                "formattedCitation": citation.formatted_citation
            })
        
        result.append({
            "id": group.id,
            "name": group.name,
            "citations": citations
        })
    
    return jsonify(result), 200


@citations_bp.route("/groups", methods=["POST"])
@csrf_protect
@login_required
def create_group(user):
    """
    Create a new citation group.
    
    Returns:
        JSON: The newly created group.
    """
    data = request.json
    name = data.get("name", "").strip()
    
    if not name:
        return jsonify({"error": "Gruppenname ist erforderlich"}), 400
    
    new_group = CitationGroup(
        user_id=user.id,
        name=name
    )
    db.session.add(new_group)
    db.session.commit()
    
    return jsonify({
        "id": new_group.id,
        "name": new_group.name,
        "citations": []
    }), 201


@citations_bp.route("/groups/<int:group_id>", methods=["PUT"])
@csrf_protect
@login_required
def update_group(user, group_id):
    """
    Update a citation group's name.
    
    Args:
        group_id: The ID of the group to update.
        
    Returns:
        JSON: The updated group.
    """
    group = CitationGroup.query.get(group_id)
    
    if not group or group.user_id != user.id:
        return jsonify({"error": "Gruppe nicht gefunden"}), 404
    
    data = request.json
    name = data.get("name", "").strip()
    
    if not name:
        return jsonify({"error": "Gruppenname ist erforderlich"}), 400
    
    group.name = name
    db.session.commit()
    
    return jsonify({
        "id": group.id,
        "name": group.name
    }), 200


@citations_bp.route("/groups/<int:group_id>", methods=["DELETE"])
@csrf_protect
@login_required
def delete_group(user, group_id):
    """
    Delete a citation group and all its citations.
    
    Args:
        group_id: The ID of the group to delete.
        
    Returns:
        JSON: Success message.
    """
    group = CitationGroup.query.get(group_id)
    
    if not group or group.user_id != user.id:
        return jsonify({"error": "Gruppe nicht gefunden"}), 404
    
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({"message": "Gruppe gelöscht"}), 200


# -------------------------------
# Citation API routes
# -------------------------------

@citations_bp.route("/groups/<int:group_id>/citations", methods=["POST"])
@csrf_protect
@login_required
def create_citation(user, group_id):
    """
    Create a new citation within a group.
    
    Args:
        group_id: The ID of the group to add the citation to.
        
    Returns:
        JSON: The newly created citation.
    """
    group = CitationGroup.query.get(group_id)
    
    if not group or group.user_id != user.id:
        return jsonify({"error": "Gruppe nicht gefunden"}), 404
    
    data = request.json
    source_type = data.get("sourceType", "").strip()
    style = data.get("style", "").strip()
    source_data = data.get("data", {})
    
    if not source_type:
        return jsonify({"error": "Quellentyp ist erforderlich"}), 400
    
    if not style:
        return jsonify({"error": "Zitierstil ist erforderlich"}), 400
    
    # Generate the formatted citation
    formatted = format_citation(style, source_type, source_data)
    
    new_citation = Citation(
        group_id=group_id,
        source_type=source_type,
        style=style,
        data=json.dumps(source_data),
        formatted_citation=formatted
    )
    db.session.add(new_citation)
    db.session.commit()
    
    return jsonify({
        "id": new_citation.id,
        "sourceType": new_citation.source_type,
        "style": new_citation.style,
        "data": source_data,
        "formattedCitation": new_citation.formatted_citation
    }), 201


@citations_bp.route("/citations/<int:citation_id>", methods=["PUT"])
@csrf_protect
@login_required
def update_citation(user, citation_id):
    """
    Update a citation.
    
    Args:
        citation_id: The ID of the citation to update.
        
    Returns:
        JSON: The updated citation.
    """
    citation = Citation.query.get(citation_id)
    
    if not citation:
        return jsonify({"error": "Zitat nicht gefunden"}), 404
    
    # Verify user owns this citation through the group
    group = CitationGroup.query.get(citation.group_id)
    if not group or group.user_id != user.id:
        return jsonify({"error": "Nicht autorisiert"}), 403
    
    data = request.json
    source_type = data.get("sourceType", citation.source_type).strip()
    style = data.get("style", citation.style).strip()
    source_data = data.get("data", json.loads(citation.data))
    
    # Regenerate the formatted citation
    formatted = format_citation(style, source_type, source_data)
    
    citation.source_type = source_type
    citation.style = style
    citation.data = json.dumps(source_data)
    citation.formatted_citation = formatted
    db.session.commit()
    
    return jsonify({
        "id": citation.id,
        "sourceType": citation.source_type,
        "style": citation.style,
        "data": source_data,
        "formattedCitation": citation.formatted_citation
    }), 200


@citations_bp.route("/citations/<int:citation_id>", methods=["DELETE"])
@csrf_protect
@login_required
def delete_citation(user, citation_id):
    """
    Delete a citation.
    
    Args:
        citation_id: The ID of the citation to delete.
        
    Returns:
        JSON: Success message.
    """
    citation = Citation.query.get(citation_id)
    
    if not citation:
        return jsonify({"error": "Zitat nicht gefunden"}), 404
    
    # Verify user owns this citation through the group
    group = CitationGroup.query.get(citation.group_id)
    if not group or group.user_id != user.id:
        return jsonify({"error": "Nicht autorisiert"}), 403
    
    db.session.delete(citation)
    db.session.commit()
    
    return jsonify({"message": "Zitat gelöscht"}), 200


@citations_bp.route("/format", methods=["POST"])
@login_required
def preview_citation(user):
    """
    Preview a formatted citation without saving.
    
    Returns:
        JSON: The formatted citation.
    """
    data = request.json
    source_type = data.get("sourceType", "").strip()
    style = data.get("style", "").strip()
    source_data = data.get("data", {})
    
    if not source_type or not style:
        return jsonify({"error": "Quellentyp und Stil sind erforderlich"}), 400
    
    formatted = format_citation(style, source_type, source_data)
    
    return jsonify({
        "formattedCitation": formatted
    }), 200
