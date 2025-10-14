package com.example.dronedilivery.ui;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.dronedilivery.R;
import com.example.dronedilivery.model.site;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class WaypointAdapter extends RecyclerView.Adapter<WaypointAdapter.VH> {

    public interface OnUseClick {
        void onUse(site site);
    }

    private final List<site> all = new ArrayList<>();
    private final List<site> visible = new ArrayList<>();
    private final OnUseClick listener;

    public WaypointAdapter(List<site> data, OnUseClick listener) {
        this.listener = listener;
        submit(data);
    }

    public void submit(List<site> data){
        all.clear(); visible.clear();
        if (data != null) {
            all.addAll(data);
            visible.addAll(data);
        }
        notifyDataSetChanged();
    }

    public void filter(String q){
        visible.clear();
        if (q == null || q.trim().isEmpty()){
            visible.addAll(all);
        } else {
            String s = q.toLowerCase(Locale.ROOT);
            for (site site : all){
                if (site.getName().toLowerCase(Locale.ROOT).contains(s)){
                    visible.add(site);
                }
            }
        }
        notifyDataSetChanged();
    }

    @NonNull @Override
    public VH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View v = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_site, parent, false);
        return new VH(v);
    }

    @Override
    public void onBindViewHolder(@NonNull VH h, int pos) {
        site s = visible.get(pos);
        h.tvName.setText(s.getName());
        h.btnUse.setOnClickListener(v -> {
            if (listener != null) listener.onUse(s);
        });
    }

    @Override
    public int getItemCount() { return visible.size(); }

    static class VH extends RecyclerView.ViewHolder {
        TextView tvName; ImageButton btnUse;
        VH(@NonNull View itemView) {
            super(itemView);
            tvName = itemView.findViewById(R.id.tvName);
            btnUse = itemView.findViewById(R.id.btnUse);
        }
    }
}
