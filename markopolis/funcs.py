from .data_dantic import (
    NoteMeta,
    NoteContent,
    ToCItem,
    ToC,
    MarkdownFileList,
    Error,
    Backlink,
    BacklinkList,
    Raw,
    Status,
    Health,
    FuzzySearchResult,
    NoteSearchFull,
)
from .md import (
    list_markdown_files,
    get_meta,
    get_note_content,
    get_toc,
    fuzzy_search_in_text,
    get_backlinks_slow,
    raw,
    create_markdown_files,
)


__all__ = ["list_md", "get_metadata", "get_note", "get_headings"]


def list_md():
    files, error = list_markdown_files()

    if files is not None:
        return MarkdownFileList(files=files)

    return Error(error=error)


def get_metadata(note_path: str) -> NoteMeta | Error:
    metadata, error = get_meta(note_path)
    if metadata is not None:
        try:
            return NoteMeta(
                title=metadata["title"],
                date=metadata["date"],
                tags=metadata["tags"],
                path=metadata["path"],
                custom_fields=metadata.get("custom_fields", {}),
            )
        except ValueError as e:
            return Error(error=f"Validation error: {str(e)}")
    return Error(error=error)


def get_note(note_path: str) -> NoteContent | Error:
    content, error = get_note_content(note_path)
    if content is not None:
        return NoteContent(markdown=content[0], html=content[1])
    return Error(error=error)


def get_headings(note_path: str) -> ToC | Error:
    toc, error = get_toc(note_path)

    def create_toc_item(title: str, children: dict) -> ToCItem:
        return ToCItem(
            title=title,
            children={k: create_toc_item(k, v) for k, v in children.items()},
        )

    if toc is not None:
        headings = {k: create_toc_item(k, v) for k, v in toc.items()}
        return ToC(headings=headings)
    return Error(error=error)


def search_full(query, max_dist):
    matches = fuzzy_search_in_text(query, max_dist)
    results = [FuzzySearchResult(file_path=m[0], snippet=m[1]) for m in matches]
    return NoteSearchFull(results=results)


def get_backlinks(note_title):
    backlinks, error = get_backlinks_slow(note_title)

    if backlinks is not None:
        blinks = [
            Backlink(title=b.split(".")[0].replace("-", " "), link=b.split(".")[0])
            for b in backlinks
        ]
        return BacklinkList(backlinks=blinks)

    return Error(error=error)


def get_raw(note_path: str) -> "Raw":
    contents, error = raw(note_path)
    if contents is not None:
        return Raw(contents=contents)
    return Raw(contents=error)


def write_files(md_dict):
    result = create_markdown_files(md_dict)

    return Status(status=result)


def health():
    return Health(status="healthy")
