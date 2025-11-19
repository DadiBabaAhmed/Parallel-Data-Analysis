"""
Graph generator for creating visualizations
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime

class GraphGenerator:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.output_dir = f"output/general/graphs"
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def generate_all_graphs(self, df, results):
        """Generate all visualization graphs"""
        # Convert a sampled Spark DataFrame to Pandas for visualization (limit to avoid OOM)
        try:
            pandas_df = df.limit(5000).toPandas()
        except Exception:
            pandas_df = None
        
        # Generate different types of graphs
        if pandas_df is not None:
            self.plot_distributions(pandas_df)
        self.plot_correlations(results.get('correlation'))
        self.plot_aggregations(results.get('aggregation'))
        self.plot_statistical_summary(results.get('statistics'))
        
        print(f"✓ Graphs saved to {self.output_dir}/")
    
    def plot_distributions(self, df):
        """Plot distribution for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return
        
        # Create subplots for each numeric column
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        if n_rows == 1:
            axes = [axes] if n_cols == 1 else axes
        else:
            axes = axes.flatten()
        
        for idx, col in enumerate(numeric_cols):
            if idx < len(axes):
                axes[idx].hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
        
        # Hide empty subplots
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/distributions_{self.timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_correlations(self, correlation_data):
        """Plot correlation heatmap"""
        if not correlation_data or 'matrix' not in correlation_data:
            return
        
        corr_matrix = pd.DataFrame(correlation_data['matrix'])
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   fmt='.2f', square=True, linewidths=1)
        plt.title('Correlation Matrix')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/correlation_{self.timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_aggregations(self, agg_data):
        """Plot aggregation results"""
        if not agg_data or 'data' not in agg_data:
            return
        
        agg_df = pd.DataFrame(agg_data['data'])
        
        # Plot average values
        avg_cols = [col for col in agg_df.columns if '_avg' in col]
        if avg_cols and len(agg_data.get('group_by', [])) > 0:
            group_col = agg_data['group_by'][0]
            
            fig, ax = plt.subplots(figsize=(12, 6))
            x = range(len(agg_df))
            width = 0.8 / len(avg_cols)
            
            for idx, col in enumerate(avg_cols):
                offset = width * idx - (width * len(avg_cols) / 2)
                ax.bar([i + offset for i in x], agg_df[col], width, label=col)
            
            ax.set_xlabel(group_col)
            ax.set_ylabel('Average Value')
            ax.set_title('Aggregated Averages by Group')
            ax.set_xticks(x)
            ax.set_xticklabels(agg_df[group_col], rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/aggregation_{self.timestamp}.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def plot_statistical_summary(self, stats_data):
        """Plot statistical summary"""
        if not stats_data or 'summary' not in stats_data:
            return
        
        summary_df = pd.DataFrame(stats_data['summary'])
        
        # Plot box plots for key statistics
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Mean values
        numeric_cols = [col for col in summary_df.columns if col != 'summary']
        means = []
        for col in numeric_cols:
            try:
                mean_val = float(summary_df.loc[summary_df['summary'] == 'mean', col].values[0])
                means.append(mean_val)
            except:
                means.append(0)
        
        axes[0].bar(range(len(numeric_cols)), means)
        axes[0].set_xticks(range(len(numeric_cols)))
        axes[0].set_xticklabels(numeric_cols, rotation=45, ha='right')
        axes[0].set_ylabel('Mean Value')
        axes[0].set_title('Mean Values by Column')
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Standard deviation
        stds = []
        for col in numeric_cols:
            try:
                std_val = float(summary_df.loc[summary_df['summary'] == 'stddev', col].values[0])
                stds.append(std_val)
            except:
                stds.append(0)
        
        axes[1].bar(range(len(numeric_cols)), stds, color='orange')
        axes[1].set_xticks(range(len(numeric_cols)))
        axes[1].set_xticklabels(numeric_cols, rotation=45, ha='right')
        axes[1].set_ylabel('Standard Deviation')
        axes[1].set_title('Standard Deviation by Column')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/statistics_{self.timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_time_series(self, df, time_col, value_col):
        """Plot time series data"""
        plt.figure(figsize=(14, 6))
        plt.plot(df[time_col], df[value_col], marker='o', linestyle='-', linewidth=2)
        plt.xlabel(time_col)
        plt.ylabel(value_col)
        plt.title(f'Time Series: {value_col} over {time_col}')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/timeseries_{self.timestamp}.png', dpi=300, bbox_inches='tight')
        plt.close()
