"""
Query Interface for Hot Parts Database
Provides user-friendly interface for querying the database and generating random parts lists.
"""

import argparse
import logging
import pandas as pd
from database_manager import DatabaseManager
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QueryInterface:
    """User-friendly interface for querying the Hot Parts database."""
    
    def __init__(self, db_path: str = "hotparts.db"):
        """Initialize query interface.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_manager = DatabaseManager(db_path)
    
    def get_random_parts_list(self, count: int = 10, min_price: float = 10.0, 
                            max_manufacturers: int = 5, output_file: str = None, 
                            output_format: str = 'excel') -> pd.DataFrame:
        """Generate a random parts list based on criteria.
        
        Args:
            count: Number of parts to return
            min_price: Minimum target price
            max_manufacturers: Maximum number of manufacturers
            output_file: Optional file to save results
            output_format: Output format ('excel', 'pdf', or 'both')
            
        Returns:
            DataFrame with random parts
        """
        logger.info(f"Generating random parts list: {count} parts, min_price=${min_price}, max_manufacturers={max_manufacturers}")
        
        # Get random parts from database
        parts_data = self.db_manager.get_random_parts(count, min_price, max_manufacturers)
        
        if not parts_data:
            logger.warning("No parts found matching criteria")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(parts_data)
        
        # Format the output
        if not df.empty:
            # Reorder columns for better readability
            column_order = [
                'mpn', 'manufacturer', 'target_price', 'excess_qty',
                'hot_parts_date', 'reqs_count', 'product_class', 
                'description', 'excess_filename'
            ]
            df = df[column_order]
            
            # Format price column
            df['target_price'] = df['target_price'].apply(lambda x: f"${x:.2f}" if x else "N/A")
            
            # Add summary statistics
            total_value = sum([float(str(p).replace('$', '')) for p in df['target_price'] if p != 'N/A'])
            total_qty = df['excess_qty'].sum()
            
            logger.info(f"Generated list with {len(df)} parts from {df['manufacturer'].nunique()} manufacturers")
            logger.info(f"Total value: ${total_value:.2f}, Total quantity: {total_qty}")
            
            # Save to file if requested
            if output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if output_format in ['excel', 'both']:
                    excel_filename = f"{output_file}_{timestamp}.xlsx"
                    df.to_excel(excel_filename, index=False)
                    logger.info(f"Saved random parts list to: {excel_filename}")
                
                if output_format in ['pdf', 'both']:
                    pdf_filename = f"{output_file}_{timestamp}.pdf"
                    title = f"Random Parts List - {count} Parts (Min Price: ${min_price})"
                    self.export_to_pdf(df, pdf_filename, title)
                    logger.info(f"Saved PDF report to: {pdf_filename}")
        
        return df
    
    def show_database_stats(self):
        """Display database statistics."""
        stats = self.db_manager.get_database_stats()
        
        print("\n" + "="*50)
        print("DATABASE STATISTICS")
        print("="*50)
        
        if stats:
            print(f"Hot Parts Records: {stats.get('hot_parts_count', 0):,}")
            print(f"Excess Inventory Records: {stats.get('excess_inventory_count', 0):,}")
            print(f"Match Records: {stats.get('matches_count', 0):,}")
            print(f"Processing Log Entries: {stats.get('processing_log_count', 0):,}")
            print()
            print(f"Unique Hot Parts MPNs: {stats.get('unique_hot_parts_mpns', 0):,}")
            print(f"Unique Excess MPNs: {stats.get('unique_excess_mpns', 0):,}")
            print(f"Unique Match MPNs: {stats.get('unique_match_mpns', 0):,}")
            print()
            print(f"Hot Parts Date Range: {stats.get('hot_parts_date_range', 'No data')}")
        else:
            print("No statistics available")
        
        print("="*50)
    
    def show_summaries(self):
        """Display data summaries."""
        print("\n" + "="*50)
        print("HOT PARTS SUMMARY")
        print("="*50)
        hot_parts_summary = self.db_manager.get_hot_parts_summary()
        if not hot_parts_summary.empty:
            print(hot_parts_summary.head(10).to_string(index=False))
        else:
            print("No hot parts data available")
        
        print("\n" + "="*50)
        print("EXCESS INVENTORY SUMMARY")
        print("="*50)
        excess_summary = self.db_manager.get_excess_summary()
        if not excess_summary.empty:
            print(excess_summary.head(10).to_string(index=False))
        else:
            print("No excess inventory data available")
        
        print("\n" + "="*50)
        print("MATCHES SUMMARY")
        print("="*50)
        matches_summary = self.db_manager.get_matches_summary()
        if not matches_summary.empty:
            print(matches_summary.head(10).to_string(index=False))
        else:
            print("No matches data available")
    
    def export_data(self, output_dir: str = "."):
        """Export database data to Excel files."""
        logger.info(f"Exporting data to: {output_dir}")
        self.db_manager.export_to_excel(output_dir)
        print(f"Data exported to {output_dir}/")
        print("- Master_Hot_Parts_Data.xlsx")
        print("- Master_Matches_Data.xlsx")
    
    def custom_query(self, query: str):
        """Execute a custom SQL query.
        
        Args:
            query: SQL query to execute
        """
        try:
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query(query, conn)
                if not df.empty:
                    print(f"\nQuery Results ({len(df)} rows):")
                    print("="*50)
                    print(df.to_string(index=False))
                else:
                    print("No results found")
        except Exception as e:
            logger.error(f"Query failed: {e}")
            print(f"Error: {e}")
    
    def export_to_pdf(self, df: pd.DataFrame, output_file: str, title: str = "Hot Parts Report"):
        """Export DataFrame to a professional PDF table.
        
        Args:
            df: DataFrame to export
            output_file: Output PDF file path
            title: Report title
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(output_file, pagesize=letter)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Add title
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Add timestamp
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            timestamp_style = ParagraphStyle(
                'Timestamp',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            story.append(Paragraph(f"Generated on {timestamp}", timestamp_style))
            story.append(Spacer(1, 12))
            
            # Add summary statistics
            if not df.empty:
                total_parts = len(df)
                unique_manufacturers = df['manufacturer'].nunique() if 'manufacturer' in df.columns else 0
                total_qty = df['excess_qty'].sum() if 'excess_qty' in df.columns else 0
                
                # Calculate total value if target_price exists
                total_value = 0
                if 'target_price' in df.columns:
                    for price in df['target_price']:
                        if isinstance(price, str) and price.startswith('$'):
                            try:
                                total_value += float(price.replace('$', ''))
                            except ValueError:
                                pass
                        elif isinstance(price, (int, float)):
                            total_value += price
                
                summary_data = [
                    ['Summary Statistics', ''],
                    ['Total Parts', str(total_parts)],
                    ['Unique Manufacturers', str(unique_manufacturers)],
                    ['Total Quantity', f"{total_qty:,}"],
                    ['Total Value', f"${total_value:,.2f}"]
                ]
                
                summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(summary_table)
                story.append(Spacer(1, 20))
            
            # Prepare data for table
            if not df.empty:
                # Convert DataFrame to list of lists for ReportLab
                data = [df.columns.tolist()]  # Header row
                for _, row in df.iterrows():
                    data.append(row.tolist())
                
                # Calculate column widths based on content
                col_widths = []
                for col in df.columns:
                    max_width = len(str(col))  # Header width
                    for value in df[col]:
                        max_width = max(max_width, len(str(value)))
                    # Set reasonable limits
                    col_width = min(max_width * 0.15, 1.5) * inch
                    col_widths.append(col_width)
                
                # Create table
                table = Table(data, colWidths=col_widths)
                
                # Style the table
                table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    
                    # Grid styling
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                    
                    # Cell padding
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(table)
            else:
                # No data message
                no_data_style = ParagraphStyle(
                    'NoData',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                story.append(Paragraph("No data available for this report", no_data_style))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(description="Hot Parts Database Query Interface")
    parser.add_argument('--db', default='hotparts.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Random parts command
    random_parser = subparsers.add_parser('random', help='Generate random parts list')
    random_parser.add_argument('--count', type=int, default=10, help='Number of parts to return')
    random_parser.add_argument('--min-price', type=float, default=10.0, help='Minimum target price')
    random_parser.add_argument('--max-manufacturers', type=int, default=5, help='Maximum number of manufacturers')
    random_parser.add_argument('--output', help='Output file name (without extension)')
    random_parser.add_argument('--format', choices=['excel', 'pdf', 'both'], default='excel', 
                              help='Output format (default: excel)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Summaries command
    subparsers.add_parser('summaries', help='Show data summaries')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to Excel')
    export_parser.add_argument('--output-dir', default='.', help='Output directory')
    
    # Custom query command
    query_parser = subparsers.add_parser('query', help='Execute custom SQL query')
    query_parser.add_argument('sql', help='SQL query to execute')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize interface
    interface = QueryInterface(args.db)
    
    # Execute command
    if args.command == 'random':
        df = interface.get_random_parts_list(
            count=args.count,
            min_price=args.min_price,
            max_manufacturers=args.max_manufacturers,
            output_file=args.output,
            output_format=args.format
        )
        if not df.empty:
            print("\nRandom Parts List:")
            print("="*80)
            print(df.to_string(index=False))
    
    elif args.command == 'stats':
        interface.show_database_stats()
    
    elif args.command == 'summaries':
        interface.show_summaries()
    
    elif args.command == 'export':
        interface.export_data(args.output_dir)
    
    elif args.command == 'query':
        interface.custom_query(args.sql)

if __name__ == "__main__":
    main() 