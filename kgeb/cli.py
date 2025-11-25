import argparse
from pathlib import Path
from .extractor import run_extraction
from .evaluator import evaluate


def main():
    parser = argparse.ArgumentParser(prog="kgeb")
    sub = parser.add_subparsers(dest='cmd')

    ex = sub.add_parser('extract')
    ex.add_argument('--docs', default=None)
    ex.add_argument('--out', default=None)

    ev = sub.add_parser('eval')
    ev.add_argument('gold_entities')
    ev.add_argument('gold_relations')
    ev.add_argument('pred_entities')
    ev.add_argument('pred_relations')
    ev.add_argument('--method', default='Method A')

    args = parser.parse_args()
    if args.cmd == 'extract':
        run_extraction(doc_path=args.docs, output_dir=args.out)
    elif args.cmd == 'eval':
        report = evaluate(Path(args.gold_entities), Path(args.gold_relations), Path(args.pred_entities), Path(args.pred_relations), method_name=args.method)
        print(report)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
