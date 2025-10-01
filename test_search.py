import sys
sys.path.insert(0, 'src')
import asyncio
from basic_memory.mcp.tools.search import search_notes

async def test_search():
    try:
        result = await search_notes.fn(query='*', page=1, page_size=5)
        print(f'Type of result: {type(result)}')
        print(f'Has results attr: {hasattr(result, "results")}')
        if hasattr(result, 'results'):
            print(f'Results type: {type(result.results)}')
            print(f'Number of results: {len(result.results)}')
            if result.results:
                first_result = result.results[0]
                print(f'First result type: {type(first_result)}')
                print(f'First result has title: {hasattr(first_result, "title")}')
                if hasattr(first_result, 'title'):
                    print(f'First result title: {first_result.title}')
        elif isinstance(result, dict):
            print(f'Result is dict with keys: {result.keys()}')
            if 'results' in result:
                print(f'Results in dict: {type(result["results"])}')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search())


